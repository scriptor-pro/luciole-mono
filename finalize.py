"""Étape 2 (fontTools) : métadonnées, features, hinting."""
import os
import sys

from fontTools.ttLib import TTFont
from fontTools.ttLib.tables import ttProgram

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import config  # noqa: E402

MODIFIED = ("Modified: monospaced version (Luciole Mono), derived from Luciole "
            "© Laurent Bourcellier & Jonathan Perez, under CC-BY 4.0.")


def set_names(font):
    name = font["name"]
    license_text = name.getDebugName(13) or ""
    full = f"{config.FAMILY} {config.STYLE}"
    values = {
        1: config.FAMILY, 2: config.STYLE, 3: f"{full};{config.PS_NAME}",
        4: full, 6: config.PS_NAME, 16: config.FAMILY, 17: config.STYLE,
        13: f"{license_text}\n\n{MODIFIED}",
    }
    name.names = [r for r in name.names if r.nameID not in values]
    for name_id, value in values.items():
        name.setName(value, name_id, 3, 1, 0x409)
        name.setName(value, name_id, 1, 0, 0)


def drop_features(font, table_tag, tags):
    """Retire des features (et leurs références dans les LangSys)."""
    if table_tag not in font:
        return
    table = font[table_tag].table
    records = table.FeatureList.FeatureRecord
    keep = [i for i, r in enumerate(records) if r.FeatureTag not in tags]
    remap = {old: new for new, old in enumerate(keep)}
    table.FeatureList.FeatureRecord = [records[i] for i in keep]
    table.FeatureList.FeatureCount = len(keep)
    for script in table.ScriptList.ScriptRecord:
        langsyses = [script.Script.DefaultLangSys] + [
            r.LangSys for r in script.Script.LangSysRecord]
        for ls in filter(None, langsyses):
            ls.FeatureIndex = [remap[i] for i in ls.FeatureIndex if i in remap]
            ls.FeatureCount = len(ls.FeatureIndex)
            if ls.ReqFeatureIndex != 0xFFFF:
                ls.ReqFeatureIndex = remap.get(ls.ReqFeatureIndex, 0xFFFF)


def strip_hinting(font):
    for tag in ("fpgm", "prep", "cvt ", "hdmx", "LTSH", "VDMX", "DSIG"):
        if tag in font:
            del font[tag]
    glyf = font["glyf"]
    for name in font.getGlyphOrder():
        g = glyf[name]
        if g.numberOfContours or g.isComposite():
            g.program = ttProgram.Program()
            g.program.fromBytecode(b"")


def fix_added_empty_glyphs(font):
    """FontForge ajoute des glyphes vides standards (nonmarkingreturn) à la
    génération : ils prennent aussi la largeur de la cellule."""
    hmtx, glyf = font["hmtx"], font["glyf"]
    for name in font.getGlyphOrder():
        if name in config.ZERO_WIDTH or glyf[name].numberOfContours:
            continue
        if hmtx[name][0] != config.CELL:
            hmtx[name] = (config.CELL, 0)


def set_mono_metadata(font):
    font["post"].isFixedPitch = 1
    font["OS/2"].panose.bProportion = 9
    font["OS/2"].xAvgCharWidth = config.CELL


def main():
    font = TTFont(os.path.join(HERE, config.STAGE1))
    set_names(font)
    drop_features(font, "GPOS", {"kern"})
    drop_features(font, "GSUB", {"liga"})
    strip_hinting(font)
    fix_added_empty_glyphs(font)
    set_mono_metadata(font)
    os.makedirs(os.path.join(HERE, "dist"), exist_ok=True)
    font.save(os.path.join(HERE, "dist", f"{config.PS_NAME}.ttf"))


if __name__ == "__main__":
    main()
