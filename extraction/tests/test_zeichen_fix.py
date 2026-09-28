import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from zeichen_fix import BROKEN_CHAR_MAP, fix_text


def test_map_has_expected_size():
    assert len(BROKEN_CHAR_MAP) == 1287


def test_di_di_ke_beispiel_aus_aufgabenstellung():
    # 䖜 -> 第 (Lektion 1: "第一課" = Lektion 1) - Vorgabe aus der Aufgabenstellung
    assert BROKEN_CHAR_MAP["䖜"] == "第"


def test_xing_familienname_gegen_seite_1_verifiziert():
    # 㿢 -> 姓, verifiziert gegen "請問貴姓" (Lektion 1, Dialog)
    assert BROKEN_CHAR_MAP["㿢"] == "姓"


def test_dong_sport_treiben_gegen_seite_3_verifiziert():
    # 䑨 -> 動, verifiziert gegen "運動" = Sport treiben (Lektion 2, Vokabeln)
    assert BROKEN_CHAR_MAP["䑨"] == "動"


def test_zai_in_gegen_seite_4_verifiziert():
    # 㸀 -> 在, verifiziert gegen die Grammatik-Erklaerung auf Seite 4
    assert BROKEN_CHAR_MAP["㸀"] == "在"


def test_mang_beschaeftigt_gegen_seite_9_verifiziert():
    # 㸟 -> 忙, verifiziert gegen "忙嗎? ... 忙 (beschaeftigt)" (Lektion 5, Dialog+Vokabeln)
    assert BROKEN_CHAR_MAP["㸟"] == "忙"


def test_piao_ticket_gegen_seite_18_verifiziert():
    # 䖻 -> 票, verifiziert gegen die viermal wiederholte Sprecher-Bezeichnung
    # "售票員" (Lektion 9, Dialog) - urspruengliche OCR-Mehrheit ("絨") war falsch,
    # durch die im Crop mitgerenderte Zhuyin-Annotation "ㄆㄧㄠˋ" korrigiert.
    assert BROKEN_CHAR_MAP["䖻"] == "票"


def test_fix_text_ersetzt_mehrere_zeichen_in_einem_string():
    text = "䖜㿢䑨"
    assert fix_text(text) == "第姓動"


def test_fix_text_laesst_unbekannte_zeichen_unveraendert():
    assert fix_text("normaler Text ohne kaputte Zeichen") == "normaler Text ohne kaputte Zeichen"


def test_kein_eintrag_bildet_auf_mehr_als_ein_zeichen_ab():
    assert all(len(correct) == 1 for correct in BROKEN_CHAR_MAP.values())
