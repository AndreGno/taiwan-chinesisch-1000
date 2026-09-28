import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pinyin_fix import fix_pinyin


def test_ziffern_symbole():
    assert fix_pinyin("W2ng F1ng xi1nsheng n0n z3o") == "Wáng Fāng xiānsheng nín zǎo"


def test_ton4_und_e_vokale():
    assert fix_pinyin("z4i k4n h7n p6ngy#u") == "zài kàn hěn péngyǒu"


def test_ton1_i_und_e():
    assert fix_pinyin("J9nti1n sh5ngr=") == "Jīntiān shēngrì"


def test_o_und_u_toene():
    assert fix_pinyin("zu@ti1n zu$ q* Ch%n h3oji&") == "zuótiān zuò qù Chūn hǎojiǔ"


def test_ue_toene():
    assert fix_pinyin("l{x0ng k3ol}") == "lǚxíng kǎolǜ"


def test_grossbuchstaben_mit_ton():
    assert fix_pinyin("~il0n `m7iz/") == "Àilín Āměizú"


def test_bindestrich_als_ton3_i():
    assert fix_pinyin("L- q-ng n- z=j- l}shu-") == "Lǐ qǐng nǐ zìjǐ lǜshuǐ"


def test_bindestrich_zwischen_silben_bleibt():
    assert fix_pinyin("x9ng-q0") == "xīng-qí"


def test_slash_und_caret_als_ton2_u():
    assert fix_pinyin("b/ji4n s/y& b^") == "bújiàn súyǔ bú"


def test_slash_nach_i_als_iu():
    assert fix_pinyin("li/ hu4 ni/r$u") == "liú huà niúròu"


def test_apostroph_bleibt():
    assert fix_pinyin("p0ng'1n n{ġ6r") == "píng'ān nǚ'ér"


def test_lektion1_sonderglyphen():
    assert fix_pinyin("FƗng hӽo wԁ Qӿngwèn hČn") == "Fāng hǎo wǒ Qǐngwèn hěn"


def test_ausrufezeichen_sind_leerraum():
    assert fix_pinyin("n0nh3o!!!!!") == "nínhǎo"


def test_klammern_bleiben():
    assert fix_pinyin("sh=(qing)") == "shì(qing)"
