# simple_test.py
def test_addition():
    assert (1 + 1) == 2, "Test failed: 1 + 1 should equal 2"

def run_tests():
    test_addition()
    print("All tests passed.")

if __name__ == "__main__":
    run_tests()