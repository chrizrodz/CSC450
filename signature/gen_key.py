import random
def gen_primes(start,stop):
	primes = [2]
	
	start = int(start)
	stop = int(stop)+1
	for i in range(3, stop+1, 2):
		is_prime = True
		for p in primes:
			if i % p == 0:
				is_prime = False
				break
		if is_prime:
			primes.append(i)
	
	return [x for x in primes if x >= start]

# Assuming a and b are both prime
def co_prime(a,b):
	for n in range(2, min(a, b) + 1):
		if a % n == b % n == 0:
			return False
	return True


def gen_key(bit_length):
	n_min = 1 << (bit_length - 1)
	n_max = (1 << bit_length) - 1

	start = 3
	stop = n_max/3

	primes = gen_primes(start,stop)

	while True:
		p = random.choice(primes)
		q = random.choice(primes)
		if n_min <= p*q <= n_max:
			break


	p_q_prod = (p-1)*(q-1)
	
	primes = gen_primes(3,p_q_prod)
	for e in primes:
		if co_prime(e,p_q_prod):
			break

	for d in range(3,p_q_prod,2):
		if (d*e-1) % p_q_prod == 0:
			break
	
	return p*q,e,d
	
			


	

