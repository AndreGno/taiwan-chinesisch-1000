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


# --- fix_span (fontabhaengig, Runde 2) ---
from zeichen_fix import fix_span

ZHUIN = "DFPBiaoKai-W5-ZhuIn-BFW-"
KAI_CHUIN = "DFKaiChuIn-Md-BPMW-BF-ET"
YUAN_CHUIN = "DFYuanChuIn-Bd-BPMW-BF-E"


def test_fix_span_lektion_1_erste_dialogzeile():
    # Seite 8 (Lektion 1), inkl. Satzzeichen Ĉ Ă Ą ĉ
    assert fix_span("㴿Ĉ䓗㸌Ă㻳䆛㴿䁍䞇Ą䱧䑻䞿㿢㳎㷵ĉ", ZHUIN) == "王：您好，我是王明華。請問貴姓大名？"


def test_fix_span_satzzeichen():
    assert fix_span("āĂăĄĈĉĊČćĞğĶķņŇƖ", ZHUIN) == "　，、。：？！…；（）「」“”→"


def test_fix_span_satzzeichen_in_chuin_font_gleich():
    assert fix_span("Ĉ", KAI_CHUIN) == "："
    assert fix_span("ăĂ", YUAN_CHUIN) == "、，"


def test_fix_span_beispiele_der_runde_1_im_zhuin_font():
    assert fix_span("䖜㿢䑨㸀㸟", ZHUIN) == "第姓動在忙"
    # 䖻 kommt nur im KaiChuIn-Font vor (Sprecher "售票員", Lektion 9)
    assert fix_span("䖻", KAI_CHUIN) == "票"


def test_fix_span_gleicher_codepoint_je_font_verschieden():
    # 㸜: im ZhuIn-Font 年 (Seite 20 u.a.), in den ChuIn-Fonts 名 (Seite 9)
    assert fix_span("㸜", ZHUIN) == "年"
    assert fix_span("㸜", YUAN_CHUIN) == "名"
    assert fix_span("㵦", KAI_CHUIN) == "王"


def test_fix_span_korrigiert_ocr_fehler_der_runde_1():
    # Tabelle Runde 1: 㳢->上, 䡉->媯; Seitenbild zeigt 才 bzw. 媽
    assert fix_span("㳢䡉", ZHUIN) == "才媽"


def test_fix_span_normale_cjk_codepoints_im_zhuin_font():
    assert fix_span("倖兼儤令䷋", ZHUIN) == "識讓聽還錢"
    assert fix_span("丈䫖", ZHUIN) == "儲蓄"


def test_fix_span_big5_level_2_nach_reserviertem_bereich():
    # 澣/澦 liegen hinter C6A1-C8FE -> ETen-Erweiterung F9D8 裏 / F9DB 粧
    assert fix_span("澣澦", ZHUIN) == "裏粧"


def test_fix_span_u3ccb_je_font():
    assert fix_span("㳋", ZHUIN) == "土"
    assert fix_span("㳋", YUAN_CHUIN) == "一"


def test_fix_span_laesst_pinyin_und_deutsch_unveraendert():
    assert fix_span("Dàw Č i ā Ɨ", "TimesNewRomanPSMT") == "Dàw Č i ā Ɨ"
    assert fix_span("m0ngzi", "PintoneTimes") == "m0ngzi"


def test_fix_span_ascii_im_hanzi_font_um_eins_zurueck():
    assert fix_span(")㸍*!2/", ZHUIN) == "(她) 1."
    assert fix_span("W,㶡", YUAN_CHUIN) == "V+句"
    assert fix_span("xbsn", KAI_CHUIN) == "warm"


def test_fix_span_jahreszahl_lektion_7():
    # Seite 20: "2:6:" + 㸜 -> 1959年 (Zhuyin/Pinyin darunter: 1 9 5 9 nián)
    assert fix_span("2:6:㸜", ZHUIN) == "1959年"


def test_fix_span_echtes_leerzeichen_bleibt():
    assert fix_span("㸜 㸜", ZHUIN) == "年 年"


def test_fix_span_unbekannter_font_laesst_echte_hanzi_stehen():
    assert fix_span("兼　", "AdobeMingStd-Light-ETen-") == "兼　"


POIN1 = "DFPBiaoKai-W5-PoIn1-BFW-"


def test_fix_span_poin_fonts_bekannte_faelle():
    assert fix_span("琞", POIN1) == "興"
    assert fix_span("炂", POIN1) == "那"
    assert fix_span("灝!", POIN1) == "弟 "
    assert fix_span("簭", "DFPBiaoKai-W5-PoIn2-BFW-") == "一"
    assert fix_span("䇅", POIN1) == "流"


def test_fix_span_poin_codepoint_je_font_verschieden():
    assert fix_span("濭", POIN1) == "奶"
    assert fix_span("濭", "DFKaiPoIn1-Md-BPMW-BF-ET") == "太"


def test_fix_span_poin_font_laesst_unbekannte_zeichen_stehen():
    assert fix_span("倖", POIN1) == "倖"


def test_fix_span_sonderfonts_zi_und_zhuyin_annotation():
    # Seite 8: "名字叫" - 字 aus eigenem Font, ġ ist nur dessen Zhuyin "ㄗ˙"
    assert fix_span("Ԇġġ", "DFBiaoKai-W5-WINP-BF-ETe") == "字"
    assert fix_span("ڗ", "DFChuIn_Kai-Md-BPMW-BF-E") == ""
    assert fix_span("ऩᎍ", "DFBiaoKai-W5-WIN-BF-ETen") == "胡適"


def test_fix_span_seitenzahl_im_mingliu_font():
    # Indexseite 8 zeigt gedruckt "1", PyMuPDF liest "2"
    assert fix_span("2", "MingLiU-ETen-B5-H") == "1"
    assert fix_span("ˤ", "MingLiU-ETen-B5-H") == "。"


def test_fix_span_ascii_verschiebung_nie_in_pinyin_oder_deutsch():
    assert fix_span("m0ngzi ji4o", "PintoneTimes") == "m0ngzi ji4o"
    assert fix_span("Guten Tag!", "TimesNewRomanPSMT") == "Guten Tag!"
    assert fix_span("Lektion 1", "ErasITC-Demi") == "Lektion 1"


def test_fix_span_echtes_zeichen_wird_nicht_nochmals_ersetzt():
    # Im ZhuIn-Font ist 䊤 das echte 兼 (Seite 93), das rohe 兼 aber 讓;
    # ebenso 㵐 -> 令, rohes 令 -> 還. Keine Verkettung der Ersetzungen.
    assert fix_span("䊤兼", ZHUIN) == "兼讓"
    assert fix_span("㵐令", ZHUIN) == "令還"
