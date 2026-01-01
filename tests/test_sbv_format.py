
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from src.generate_transcript import srt_to_sbv

def test_srt_to_sbv():
    srt_input = """1
00:00:00,000 --> 00:00:08,000
No niin, morjesta vaan. Mä oon Sami Miettinen, neuvottelija.

2
00:00:08,000 --> 00:00:17,000
Oon työkseni tämmöisessä Translink Corporate Finance kansainvälisessä yrityskauppaketjussa, jossa on 600 asiantuntijaa.
"""

    expected_sbv_start = """00:00:00.000,00:00:08.000
No niin, morjesta vaan. Mä oon Sami Miettinen, neuvottelija.

00:00:08.000,00:00:17.000
Oon työkseni tämmöisessä Translink Corporate Finance kansainvälisessä yrityskauppaketjussa, jossa on 600 asiantuntijaa."""

    result = srt_to_sbv(srt_input)
    print("RESULT:\n" + result)
    
    assert "00:00:00.000,00:00:08.000" in result
    assert "00:00:08.000,00:00:17.000" in result
    
    if result.strip() == expected_sbv_start.strip():
        print("\nTEST PASSED: Exact match!")
    else:
        print("\nTEST FAILED: Result does not match expected output exactly (ignoring whitespace).")
        # print differences?
        
if __name__ == "__main__":
    test_srt_to_sbv()
