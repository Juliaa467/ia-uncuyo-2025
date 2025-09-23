PYTHON=python3
SCRIPT=main.py

exp:
	$(PYTHON) $(SCRIPT) --mode exp --max_states 50000

hc:
	$(PYTHON) $(SCRIPT) --mode single --alg HC --n 8 --max_states 10000 --seed 0 --history

sa:
	$(PYTHON) $(SCRIPT) --mode single --alg SA --n 8 --max_states 20000 --seed 1 --sa_T0 2.0 --sa_alpha 0.997 --sa_Tmin 1e-5 --history

ga:
	$(PYTHON) $(SCRIPT) --mode single --alg GA --n 10 --max_states 50000 --seed 2 --ga_pop 150 --ga_k 3 --ga_pc 0.9 --ga_pm 0.1 --ga_elitism 2 --history

rand:
	$(PYTHON) $(SCRIPT) --mode single --alg random --n 8 --max_states 50000 --seed 3 --history
