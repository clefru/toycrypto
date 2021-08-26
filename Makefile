SRCS = asymmetric.py base.py ec.py gfpof.py pof.py primefields.py

TESTS = asymmetric_test.py base_test.py gfpof_test.py pof_test.py primefields_test.py

unittests:
	for i in ${TESTS}; do python $$i; done

type:
	mypy --strict ${SRCS}

format:
	for i in ${SRCS} ${TESTS}; do yapf -i --style '{based_on_style: google, indent_width: 2}' $$i; done
