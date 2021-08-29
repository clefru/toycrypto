SRCS = toycrypto/asymmetric.py toycrypto/base.py toycrypto/ec.py toycrypto/gfpof.py toycrypto/pof.py toycrypto/primefields.py

TESTS = tests/asymmetric_test.py tests/base_test.py tests/gfpof_test.py tests/pof_test.py tests/primefields_test.py tests/ec_test.py

unittests:
	for i in ${TESTS}; do python $$i; done

type:
	mypy --strict ${SRCS}

format:
	for i in ${SRCS} ${TESTS}; do yapf -i --style '{based_on_style: google, indent_width: 2}' $$i; done
