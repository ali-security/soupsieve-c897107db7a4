"""Test attribute selectors."""
import signal
import time
import soupsieve as sv
from .. import util


class TestAttribute(util.TestCase):
    """Test attribute selectors."""

    MARKUP = """
    <div id="div">
    <p id="0">Some text <span id="1"> in a paragraph</span>.</p>
    <a id="2" href="http://google.com">Link</a>
    <span id="3">Direct child</span>
    <pre id="pre">
    <span id="4">Child 1</span>
    <span id="5">Child 2</span>
    <span id="6">Child 3</span>
    </pre>
    </div>
    """

    def test_attribute_not_equal_no_quotes(self):
        """Test attribute with value that does not equal specified value (no quotes)."""

        # No quotes
        self.assert_selector(
            self.MARKUP,
            'body [id!=\\35]',
            ["div", "0", "1", "2", "3", "pre", "4", "6"],
            flags=util.HTML5
        )

    def test_attribute_not_equal_quotes(self):
        """Test attribute with value that does not equal specified value (quotes)."""

        # Quotes
        self.assert_selector(
            self.MARKUP,
            "body [id!='5']",
            ["div", "0", "1", "2", "3", "pre", "4", "6"],
            flags=util.HTML5
        )

    def test_attribute_not_equal_double_quotes(self):
        """Test attribute with value that does not equal specified value (double quotes)."""

        # Double quotes
        self.assert_selector(
            self.MARKUP,
            'body [id!="5"]',
            ["div", "0", "1", "2", "3", "pre", "4", "6"],
            flags=util.HTML5
        )

    def test_bad_attribute_unclused(self):
        """Test bad attribute fails for syntax error, not timeout error."""

        # An unterminated attribute value, quoted in either style or unquoted,
        # must fail with a syntax error instead of backtracking excessively.
        selectors = ['[a="' + ('x' * 300), "[a='" + ('x' * 300), '[a=' + ('x' * 300)]

        if hasattr(signal, 'SIGALRM'):
            # Enforce a hard timeout so a catastrophically backtracking
            # pattern aborts instead of hanging the test run.
            def timeout_handler(signum, frame):
                """Raise a timeout error when the alarm fires."""

                raise TimeoutError

            original_handler = signal.signal(signal.SIGALRM, timeout_handler)
            try:
                for selector in selectors:
                    passed = False
                    signal.alarm(3)
                    try:
                        with self.assertRaises(sv.SelectorSyntaxError):
                            sv.compile(selector)
                        passed = True
                    except TimeoutError:
                        pass
                    finally:
                        signal.alarm(0)
                    self.assertTrue(passed)
            finally:
                signal.signal(signal.SIGALRM, original_handler)
        else:
            # `SIGALRM` is not available (e.g. Windows), so time the operation instead.
            for selector in selectors:
                start = time.perf_counter()
                with self.assertRaises(sv.SelectorSyntaxError):
                    sv.compile(selector)
                self.assertTrue((time.perf_counter() - start) < 3)
