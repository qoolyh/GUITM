import gensim

model = gensim.models.KeyedVectors.load_word2vec_format('GoogleNews-vectors-negative300.bin', binary=True, limit= 500000)

sim = model.similarity("Create", "Sign")

print(sim)

sim = model.similarity("Create", "up")

print(sim)

sim = model.similarity("Create", "with")

print(sim)

sim = model.similarity("Create", "Email")

print(sim)

sim = model.similarity("Account", "Sign")

print(sim)

sim = model.similarity("Account", "up")

print(sim)

sim = model.similarity("Account", "with")

print(sim)

sim = model.similarity("Account", "Email")

print(sim)
