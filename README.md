# Knight Models for Tabletop Simulator

This folder contains simple low-poly OBJ+PNG models for French and English knights.

## Files

Each knight has its own `.obj` (mesh), `.mtl` (material reference), and `.png` (texture).

- French
  - `french_blue_knight.obj` + `french_blue_knight.png` — blue armour, gold plume
  - `french_red_knight.obj` + `french_red_knight.png` — red armour, gold plume
- English
  - `english_white_knight.obj` + `english_white_knight.png` — white armour, red plume
  - `english_black_knight.obj` + `english_black_knight.png` — black armour, red plume
- `generate_knights.py` — script that built the files

## How to add them to Tabletop Simulator

Tabletop Simulator requires two URLs for a Custom Model:
- **Model/Mesh:** a `.obj` file
- **Diffuse/Image:** a `.png` or `.jpg` file (this is the texture, not the `.mtl`)

1. In TTS: **Objects → Components → Custom → Custom Model**.
2. Paste the **raw `.obj` URL** into the **Model/Mesh** field.
3. Paste the matching **raw `.png` URL** into the **Diffuse/Image** field.
4. Press **Import**.
5. Scale the spawned knight down to about **0.1–0.25** (the model is 1 unit tall).
6. Right-click → **Save Object** so you can spawn it again later.

## Direct URLs from this repo

| Knight | Model/Mesh URL | Diffuse/Image URL |
|--------|----------------|-------------------|
| French Blue | `https://raw.githubusercontent.com/CodytTorgerson/knight-models-for-tts/master/french_blue_knight.obj` | `https://raw.githubusercontent.com/CodytTorgerson/knight-models-for-tts/master/french_blue_knight.png` |
| French Red | `https://raw.githubusercontent.com/CodytTorgerson/knight-models-for-tts/master/french_red_knight.obj` | `https://raw.githubusercontent.com/CodytTorgerson/knight-models-for-tts/master/french_red_knight.png` |
| English White | `https://raw.githubusercontent.com/CodytTorgerson/knight-models-for-tts/master/english_white_knight.obj` | `https://raw.githubusercontent.com/CodytTorgerson/knight-models-for-tts/master/english_white_knight.png` |
| English Black | `https://raw.githubusercontent.com/CodytTorgerson/knight-models-for-tts/master/english_black_knight.obj` | `https://raw.githubusercontent.com/CodytTorgerson/knight-models-for-tts/master/english_black_knight.png` |

## Tips

- If the model looks too shiny, lower the **Specular Intensity** in TTS's Material tab.
- The `.mtl` files are kept alongside the `.obj` files for compatibility, but TTS only uses the `.png` you paste into the **Diffuse/Image** field.
- For more detail, import the `.obj` into Blender and paint a custom texture, then re-export.
