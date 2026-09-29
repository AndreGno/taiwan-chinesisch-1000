import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from lektion_parser import (  # noqa: E402
    de_bereinigen, dekodiere_zeichen, parse_lektion, pinyin_anhaengen,
    pinyin_aus_zeichen, vokabeln_aus_zeile, zeichen_aus_seite, zeilen_bilden,
    zh_bereinigen,
)

# Test-Fonts beginnen mit "DF" (ASCII-Verschiebung greift), stehen aber in
# keiner Big5-Tabelle von fix_span, damit echte Hanzi unverändert bleiben.
HANZI = "DFTestKai"
YUAN = "DFYuanTest"
PINYIN = "PintoneTimes"
TNR = "TimesNewRomanPSMT"


def span(text, font, size, x, y):
    """Span im rawdict-Format; Hanzi so breit wie die Schriftgröße, Rest halb."""
    chars = []
    for c in text:
        breite = size if ord(c) > 0x2000 else size / 2
        chars.append({"c": c, "origin": (x, y), "bbox": (x, y - size, x + breite, y)})
        x += breite
    return {"font": font, "size": size, "chars": chars}


def seite(*spans):
    return {"blocks": [{"lines": [{"spans": list(spans)}]}]}


# --- Einzelfunktionen ------------------------------------------------------

def test_dekodieren_verschiebt_ascii_in_df_fonts():
    assert "".join(dekodiere_zeichen(c, HANZI) for c in "2/!3/") == "1. 2."
    assert "".join(dekodiere_zeichen(c, HANZI) for c in ")*@\"") == "()?!"
    assert "".join(dekodiere_zeichen(c, HANZI) for c in "F.nbjm") == "E-mail"
    assert "".join(dekodiere_zeichen(c, HANZI) for c in "2:6:") == "1959"


def test_dekodieren_laesst_andere_fonts_unveraendert():
    assert dekodiere_zeichen("2", TNR) == "2"
    assert dekodiere_zeichen("!", "SZenKai-Medium-ETen-B5-H") == " "


def test_zh_bereinigen_luecken_pfeile_und_fuellzeichen():
    assert zh_bereinigen("練習：1.請問那個人叫（\u3000     \u3000）？") == "練習：1.請問那個人叫（　）？"
    assert zh_bereinigen("那 ......") == "那……"
    assert zh_bereinigen("我姓方，名字叫大偉 →我叫方大偉。") == "我姓方，名字叫大偉 → 我叫方大偉。"
    assert zh_bereinigen("(游)泳衣") == "（游）泳衣"


def test_zh_bereinigen_behaelt_leerzeichen_zwischen_lateinischen_woertern():
    assert zh_bereinigen("我用 Skype 跟他說 wie viel") == "我用Skype跟他說wie viel"


def test_de_bereinigen_ligaturen_und_leerraum():
    assert de_bereinigen("im \x03 achen  Wasser") == "im flachen Wasser"
    assert de_bereinigen("Ich \x02 nde es\u3000nicht. ") == "Ich finde es nicht."


def _zeichen(text, font, size=10, x=0):
    return zeichen_aus_seite(seite(span(text, font, size, x, 100)))


def test_pinyin_ausrufezeichen_ist_o_mit_strich():
    assert pinyin_aus_zeichen(_zeichen("du!shao qi2n", PINYIN)) == "duōshao qián"


def test_pinyin_jahreszahl_aus_df_font():
    zeichen = _zeichen("W# sh= ", PINYIN) + _zeichen("2!:!6!:", HANZI, x=40)
    assert pinyin_aus_zeichen(zeichen) == "Wǒ shì 1959"


def test_pinyin_trennstrich_verbindet_folgezeile():
    assert pinyin_anhaengen("xià yì bān shí-", "hou kāi") == "xià yì bān shíhou kāi"
    assert pinyin_anhaengen("fùchū duō -", "shao") == "fùchū duōshao"
    assert pinyin_anhaengen("", "nǐ hǎo") == "nǐ hǎo"


def test_zeilen_nach_grundlinie_und_x():
    zeichen = zeichen_aus_seite(seite(
        span("B", TNR, 13, 200, 101), span("A", TNR, 13, 100, 100),
        span("C", TNR, 13, 100, 130)))
    zeilen = zeilen_bilden(zeichen)
    assert ["".join(z["c"] for z in zeile) for zeile in zeilen] == ["AB", "C"]


def test_vokabelzeile_mit_zwei_eintraegen():
    zeile = zeilen_bilden(zeichen_aus_seite(seite(
        span("時候!", HANZI, 14, 87, 100), span("sh0hou", PINYIN, 10, 120, 100),
        span("!!!!!", HANZI, 14, 160, 100), span("die Zeit", TNR, 13, 200, 100),
        span("哪兒!", HANZI, 14, 300, 100), span("n3r", PINYIN, 10, 330, 100),
        span("!!!!!xp@", HANZI, 14, 350, 100))))[0]
    assert vokabeln_aus_zeile(zeile) == [
        {"zh": "時候", "pinyin": "shíhou", "de": "die Zeit"},
        {"zh": "哪兒", "pinyin": "nǎr", "de": "wo?"},
    ]


# --- Ganze Lektion (synthetisch) --------------------------------------------

def _beispiel_lektion():
    s1 = seite(
        span("第一課!!!!自我介紹", HANZI, 22, 160, 60),
        span("Lektion 1        Sich selbst vorstellen", "ErasITC-Demi", 14, 56, 100),
        span("!!!!!!!!!!", "SZenKai-Medium-ETen-B5-H", 12, 90, 165),
        span("王先生：我要去台北，請問下一班火車什麼時", HANZI, 15, 87, 185),
        span("W2ng xi1nsheng", PINYIN, 10, 85, 210),
        span("W#  y4o q* T2ib7i q-ngw8n xi4 y= b1n hu#ch5 sh6nme sh0", PINYIN, 10, 160, 210),
        span("-", TNR, 14, 480, 210),
        span("!!!!!!!!!!!!", HANZI, 15, 87, 230), span("候開？", HANZI, 15, 190, 230),
        span("hou  k1i", PINYIN, 10, 190, 250),
        span("王：", HANZI, 15, 87, 280), span("好。", HANZI, 15, 117, 280),
        span("W2ng", PINYIN, 10, 85, 300), span("H3o", PINYIN, 10, 120, 300),
        span("台北", HANZI, 14, 87, 600), span("T2ib7i", PINYIN, 10, 120, 600),
        span("!!!!!", HANZI, 14, 160, 600), span("Taipeh", TNR, 13, 200, 600),
        span("單程票!", HANZI, 14, 87, 625), span("d1nch6ng pi4o", PINYIN, 10, 135, 625),
        span("die Fahrkarte für eine", TNR, 13, 200, 625),
        span("einfache Fahrt", TNR, 13, 200, 645),
        span("28", "MingLiU-ETen-B5-H", 10, 300, 830),
    )
    s2 = seite(
        span("!!!!!!!!!!", HANZI, 14, 56, 100), span("多少!", YUAN, 14, 90, 100),
        span("//////!", YUAN, 14, 120, 100),
        span("說明：表示疑問的用法，用來詢問", HANZI, 14, 87, 120),
        span("!!!!!!!!!!!!數量。", HANZI, 14, 87, 140),
        span("例句：!2/一張票多少錢？", HANZI, 14, 87, 160),
        span("\u3000\u3000\u30003/從這兒到那裡要多少時間？", HANZI, 14, 87, 180),
        span("練習：!2/這件衣服多少（\u3000!!!!\u3000）？", HANZI, 14, 87, 200),
        span("!!!!!!!!!!!!!!→這件衣服多少錢。", HANZI, 14, 87, 220),
        span("王先生：", HANZI, 14, 56, 700),
        span("Ich will nach Taipeh fahren. Wann fährt", TNR, 14, 120, 700),
        span("\u3000\u3000\u3000\u3000", HANZI, 14, 56, 720), span("der Zug?", TNR, 14, 120, 720),
        span("王：", HANZI, 14, 56, 740), span("Gut.", TNR, 14, 120, 740),
    )
    return parse_lektion(1, s1, s2)


def test_lektion_kopf_und_dialog():
    lektion, hinweise = _beispiel_lektion()
    assert hinweise == []
    assert lektion["titel_zh"] == "自我介紹"
    assert lektion["titel_de"] == "Sich selbst vorstellen"
    assert lektion["dialog"] == [
        {"sprecher": "王先生", "zh": "我要去台北，請問下一班火車什麼時候開？",
         "pinyin": "Wǒ yào qù Táiběi qǐngwèn xià yì bān huǒchē shénme shíhou kāi",
         "de": "Ich will nach Taipeh fahren. Wann fährt der Zug?"},
        {"sprecher": "王", "zh": "好。", "pinyin": "Hǎo", "de": "Gut."},
    ]


def test_lektion_vokabeln_mit_folgezeile():
    lektion, _ = _beispiel_lektion()
    assert lektion["vokabeln"] == [
        {"zh": "台北", "pinyin": "Táiběi", "de": "Taipeh"},
        {"zh": "單程票", "pinyin": "dānchéng piào", "de": "die Fahrkarte für eine einfache Fahrt"},
    ]


def test_lektion_grammatik():
    lektion, _ = _beispiel_lektion()
    assert lektion["grammatik"] == [{
        "titel": "多少……",
        "erklaerung": "表示疑問的用法，用來詢問數量。",
        "beispiele": ["一張票多少錢？", "從這兒到那裡要多少時間？"],
        "uebungen": ["這件衣服多少（　）？ → 這件衣服多少錢。"],
    }]


def test_vokabel_anliegende_df_zeichen_bleiben_im_feld():
    zeile = zeilen_bilden(zeichen_aus_seite(seite(
        span("投", HANZI, 14, 87, 100), span("t@u", PINYIN, 10, 110, 100),
        span(")", HANZI, 14, 160, 100), span("ein", TNR, 13, 167, 100),
        span("*", HANZI, 14, 186.5, 100), span("werfen", TNR, 13, 193.5, 100),
        span("大飽口福", HANZI, 14, 300, 100), span("d4b3o", PINYIN, 10, 360, 100),
        span(".", HANZI, 14, 385, 100), span("k#uf/", PINYIN, 10, 392, 100),
        span("genießen", TNR, 13, 450, 100))))[0]
    assert vokabeln_aus_zeile(zeile) == [
        {"zh": "投", "pinyin": "tóu", "de": "(ein)werfen"},
        {"zh": "大飽口福", "pinyin": "dàbǎo-kǒufú", "de": "genießen"},
    ]


def test_vokabel_folgezeile_mit_pinyin_und_deutsch():
    s1 = seite(
        span("王：好。", HANZI, 15, 87, 185),
        span("鞋跟", HANZI, 14, 87, 600), span("xi6 g5n", PINYIN, 10, 120, 600),
        span("der Schuhabsatz", TNR, 13, 170, 600),
        span("一分錢，一分貨", HANZI, 14, 300, 600), span("y= f5n qi2n y= f5n", PINYIN, 10, 400, 600),
        span("hu$", PINYIN, 10, 87, 625), span("Qualität hat ihren Preis", TNR, 13, 120, 625),
        span("低", HANZI, 14, 300, 625), span("d9", PINYIN, 10, 320, 625),
        span("niedrig", TNR, 13, 350, 625))
    lektion, _ = parse_lektion(3, s1, seite())
    assert lektion["vokabeln"] == [
        {"zh": "鞋跟", "pinyin": "xié gēn", "de": "der Schuhabsatz"},
        {"zh": "一分錢，一分貨", "pinyin": "yì fēn qián yì fēn huò", "de": "Qualität hat ihren Preis"},
        {"zh": "低", "pinyin": "dī", "de": "niedrig"},
    ]


def test_lektion_meldet_fehlende_uebersetzung():
    s1 = seite(span("王：好。", HANZI, 15, 87, 185))
    lektion, hinweise = parse_lektion(2, s1, seite())
    assert lektion["dialog"][0]["de"] == ""
    assert hinweise == ["Dialogzeilen 1 != Übersetzungen 0"]


# --- Abgleich mit dem echten PDF (Lektion 1, Werte aus dem Handbeispiel) ----

PDF = Path(r"D:\(x)Taiwan CN DE Lernen\1000zhtw_de.pdf")


@pytest.mark.skipif(not PDF.exists(), reason="PDF nicht vorhanden")
def test_lektion_1_aus_pdf():
    import pymupdf
    doc = pymupdf.open(PDF)
    lektion, hinweise = parse_lektion(1, doc[8].get_text("rawdict"), doc[9].get_text("rawdict"))
    assert hinweise == []
    assert (lektion["titel_zh"], lektion["titel_de"]) == ("自我介紹", "Sich selbst vorstellen")
    assert [d["zh"] for d in lektion["dialog"]] == [
        "您好，我是王明華。請問貴姓大名？", "您好，我姓方，名字叫大偉。",
        "方先生，很高興認識您。", "我也是。那位小姐是誰？",
        "她叫趙小梅，是我的同事。", "那位先生是誰？", "他叫王大方，是我的弟弟。"]
    assert [d["sprecher"] for d in lektion["dialog"]] == ["王", "方"] * 3 + ["王"]
    assert lektion["dialog"][0]["pinyin"].startswith("Nín hǎo wǒ shì Wáng Mínghuá")
    assert lektion["dialog"][6]["de"] == "Er heißt Wang, Ta-Fang. Er ist mein jüngerer Bruder."
    assert [(v["zh"], v["pinyin"]) for v in lektion["vokabeln"]][:5] == [
        ("您好", "nínhǎo"), ("我", "wǒ"), ("貴姓", "guìxìng"), ("名字", "míngzi"),
        ("叫", "jiào")]
    assert lektion["vokabeln"][8]["de"] == "das Fräulein, die Frau, die Dame"
    assert len(lektion["vokabeln"]) == 12
    assert [g["titel"] for g in lektion["grammatik"]] == ["那……", "姓……名字叫……"]
