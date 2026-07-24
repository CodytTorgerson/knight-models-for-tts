# Knight Models for Tabletop Simulator

This folder contains simple low-poly OBJ+MTL models for French and English knights.

## Files

- `french_knights.obj` / `french_knights.mtl`
  - `french_knight_blue` — blue armour, gold plume
  - `french_knight_red` — red armour, gold plume
- `english_knights.obj` / `english_knights.mtl`
  - `english_knight_white` — white/light-grey armour, red plume
  - `english_knight_black` — black/dark-grey armour, red plume
- `generate_knights.py` — script that built the OBJ/MTL files (optional, only if you want to tweak them)

## How to add them to Tabletop Simulator

1. **Place the files where TTS can see them.**
   The easiest way is to upload the `.obj` and `.mtl` files to a public cloud folder and get a direct URL for each file.  TTS cannot load models from your local disk unless you run a local web server.

   - Upload `french_knights.obj` and `french_knights.mtl` to the same folder and make them public.
   - Do the same for `english_knights.obj` and `english_knights.mtl`.

2. **In Tabletop Simulator:**
   - Open a game/table.
   - Go to **Objects → Components → Custom → Model**.
   - (Or right-click on the table and choose **Custom Model** depending on your TTS version.)
   - In the custom model dialog, paste the URL for the `.obj` file into the **Model/Mesh** field.
   - Paste the matching `.mtl` URL into the **Material** / **Diffuse** field if TTS asks for one.
   - Set **Type** to **Assetbundle** or leave it as the default OBJ/Model option.
   - Press **Import**.

3. **Scale the figure.**
   Knights are roughly 1 unit tall in the model.  In TTS, that is far too big.  After spawning, scale the object down to something like **0.1–0.25** on X/Y/Z.  Use the gizmo or the object context menu (hover and press the number keys / right-click → Scale).

4. **Set the material variant.**
   Each OBJ contains several material groups.  TTS will use the first material by default.  To change which knight skin appears, you currently need to make copies of the OBJ/MTL that reference only the desired material, or use TTS’s material override after import.  A simpler approach is already prepared: the MTL defines `french_knight_blue`, `french_knight_red`, etc.  TTS lets you swap materials on a custom object once it is in the scene.

5. **Save the object.**
   Once you are happy with scale and colour, right-click the model and choose **Save Object** so you can spawn it again from your Saved Objects chest later.

## Tips

- Keep `.obj` and `.mtl` in the same directory/URL folder; the OBJ references the MTL by filename only.
- If textures look too shiny, edit the `Ns` value in the MTL file (lower = less shiny).
- To make the models look more detailed, import them into Blender and add texture paint/team decals, then re-export as `.obj` with a single material per variant.
