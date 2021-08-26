SRCS = asymmetric.py base.py ec.py gfpof.py pof.py primefields.py

TESTS = asymmetric_tests.py base_tests.py gfpof_tests.py pof_tests.py primefields_test.py

unittests:
	for i in ${TESTS}; do python $$i; done

type:
	mypy --strict ${SRCS}

format:
	for i in ${SRCS} ${TESTS}; do yapf -i --style '{based_on_style: google, indent_width: 2}' $$i; done
