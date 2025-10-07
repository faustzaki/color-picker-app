import streamlit as st
from PIL import Image
import numpy as np
import pandas as pd

# ---- Konfigurasi Halaman ----
st.set_page_config(
    page_title="RGB Color Picker_51422646",
    layout="wide",
)

st.title("RGB Color Picker")
st.title("Faustzaki Ghathaf R - 50422540")
st.write("Upload gambar, lihat sampel warna dalam format grid, dan klik gambar untuk mengetahui warna di titik tertentu.")

# ---- Fungsi Helper untuk Warna Teks ----
def get_text_color(hex_color):
    """Menentukan warna teks (hitam/putih) berdasarkan kecerahan warna latar."""
    hex_color = hex_color.lstrip('#')
    r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    # Formula standar untuk menghitung luminance (kecerahan)
    luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
    return 'white' if luminance < 0.5 else 'black'

# ---- Upload Gambar ----
uploaded_file = st.file_uploader("Unggah gambar (PNG, JPG, JPEG)", type=["png", "jpg", "jpeg"])

if uploaded_file:
    # Baca gambar dan ubah ke RGB
    img = Image.open(uploaded_file).convert("RGB")

    # Resize untuk tampilan (agar tidak terlalu besar di Streamlit)
    max_display_width = 800
    ratio = max_display_width / img.width if img.width > max_display_width else 1
    display_img = img.resize((int(img.width * ratio), int(img.height * ratio)))
    img_array = np.array(display_img)
    height, width, _ = img_array.shape

    st.info(f"**Ukuran tampilan:** {width} × {height} — (dari ukuran asli {img.width} × {img.height})")

    # ---- Layout ----
    col1, col2 = st.columns([2, 1], gap="large")

    with col1:
        from streamlit_image_coordinates import streamlit_image_coordinates

        st.write("Klik di dalam gambar untuk melihat warna pada koordinat tertentu:")
        coords = streamlit_image_coordinates(display_img, key="color_picker")

        if coords is not None:
            x, y = int(coords["x"]), int(coords["y"])
            if 0 <= x < width and 0 <= y < height:
                color = tuple(map(int, img_array[y, x]))
                hex_color = "#{:02x}{:02x}{:02x}".format(*color)

                st.success(
                    f"**Koordinat:** ({x}, {y})  \n"
                    f"**RGB:** {color}  \n"
                    f"**HEX:** {hex_color}"
                )

                # Preview warna
                st.markdown(
                    f"""<div style='
                        width:100px;
                        height:50px;
                        background:{hex_color};
                        border-radius:8px;
                        border:1px solid #aaa;
                        color:{get_text_color(hex_color)};
                        display:flex;
                        justify-content:center;
                        align-items:center;
                        font-family:monospace;
                        font-weight:bold;'>
                        {hex_color}
                    </div>""",
                    unsafe_allow_html=True
                )

    with col2:
        st.subheader("Grid Sampel Warna")
        step = st.slider("Sampling pixel setiap:", 5, 100, 25, help="Semakin besar nilainya, semakin kecil gridnya dan semakin ringan prosesnya.")
        
        # ---- Membuat Data Grid ----
        grid_data = []
        # Iterasi berdasarkan step untuk mengambil sampel
        for y in range(0, height, step):
            row_data = []
            for x in range(0, width, step):
                r, g, b = img_array[y, x]
                hex_color = f"#{r:02x}{g:02x}{b:02x}"
                row_data.append(hex_color)
            grid_data.append(row_data)

        # Membuat label untuk kolom dan baris (index)
        x_labels = [str(x) for x in range(0, width, step)]
        y_labels = [str(y) for y in range(0, height, step)]
        
        df_grid = pd.DataFrame(grid_data, index=y_labels, columns=x_labels)

        # ---- Styling Tabel ----
        def style_cell(hex_code):
            """Memberi style background dan warna teks pada setiap sel."""
            text_color = get_text_color(hex_code)
            return f'background-color: {hex_code}; color: {text_color}; font-family: monospace; font-size: 12px;'

        # Menampilkan DataFrame dengan style
        st.dataframe(df_grid.style.applymap(style_cell), use_container_width=True)
        st.caption(f"Menampilkan grid warna dengan sampel setiap {step} pixel. Kolom = X, Baris = Y.")
        
        # ---- Tombol Download (Data tetap dalam format panjang) ----
        coords_long = [(x, y) for y in range(0, height, step) for x in range(0, width, step)]
        colors_long = [tuple(map(int, img_array[y, x])) for (x, y) in coords_long]
        hex_colors_long = ["#{:02x}{:02x}{:02x}".format(r, g, b) for r, g, b in colors_long]

        df_long = pd.DataFrame(coords_long, columns=["X", "Y"])
        df_long["RGB"] = colors_long
        df_long["HEX"] = hex_colors_long
        
        csv = df_long.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download semua data warna (CSV)",
            data=csv,
            file_name="color_samples.csv",
            mime="text/csv",
        )

else:
    st.warning("Silakan unggah gambar terlebih dahulu untuk memulai analisis.")