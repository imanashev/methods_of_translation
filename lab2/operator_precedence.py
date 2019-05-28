import sys
import shlex
import csv

# def read_grammar(grammar):


def parse(F,G,operators, sentence):
	sentence = sentence + '$'
	stack = []
	stack.append('$')
	pos = 0
	while True:
		print(stack, sentence[pos:])
		if sentence[pos] == '$' and stack[-1] == '$':
			print('Accepted')
			return

		top = stack[-1]
		curent = sentence[pos]
		print('top', top)

		top_weight = F[operators.index(str(top))]
		current_weight = G[operators.index(str(curent))]

		# if self.pre_matrix.get((top, sentence[pos]), None) in ['=', '<']:
		if top_weight <= current_weight:
			stack.append(sentence[pos])
			pos += 1
		# elif self.pre_matrix.get((top, sentence[pos]), None) == '>':
		else:
			while True:
				p = stack.pop()
				top = stack[-1]
				print(stack, sentence[pos:])

				p_weight = G[operators.index(str(p))]
				top_weight = F[operators.index(str(top))]

				if top < p:
				# if self.pre_matrix.get((top, p), None) == '<':
					break
				elif top == sentence[pos] == '$':
					break
				# elif (top, p) not in self.pre_matrix:
					# print(top, sentence[pos], 'Not Accepted!')
					# return
		# else:
		# 	print('Not Accepted')
		# 	return



def main():
	
	# input_string = "i + i - i"
	input_string = open('input1.txt', 'r')
	input_string = input_string.read()
	input_ind = list(shlex.shlex(input_string))
	input_ind.append('$')
	
	## Grammar reading
	master = {}
	master_list = []
	new_list = []
	non_terminals = []
	grammar = open('grammar1.txt', 'r')
	
	for row2 in grammar:
		
		if '->' in row2:
			#new production
			if len(new_list) == 0:
				start_state = row2[0]
				non_terminals.append(row2[0])
				new_list = []
				new_list.append(row2.rstrip('\n'))
			else:
				master_list.append(new_list)
				del new_list
				new_list = []
				new_list.append(row2.rstrip('\n'))
				non_terminals.append(row2[0])
				
		
		elif '|' in row2:
			new_list.append(row2.rstrip('\n'))	
	
	master_list.append(new_list)
	
	
	for x in xrange(len(master_list)):
		for y in xrange(len(master_list[x])):
			master_list[x][y] = [s.replace('|', '') for s in master_list[x][y]]
			master_list[x][y] = ''.join(master_list[x][y])
			master[master_list[x][y]] = non_terminals[x] 

	for key, value in master.iteritems():
		if '->' in key:
			length = len(key)
			for i in xrange(length):
				if key[i] == '-' and key[i + 1] == ">":
					index =  i+2
					break
			var_key = key
			new_key = key[index:]
	
	var = master[var_key]
	del master[var_key]
	master[new_key] = var	
	
    ## Precedence matrix reading
	order_table = []
	with open('order1.csv', 'rU') as file2:
		order = csv.reader(file2)
		for row in order:
			order_table.append(row)
	
	operators = order_table[0]

	print "Precedence matrix"
	print('\n'.join(['\t'.join([str(cell) for cell in row]) for row in order_table]) + '\n')

    ## Precedence functions genertion
	f = [1] * len(operators)
	g = [1] * len(operators)

	is_changed = 1
	while is_changed:
		is_changed = 0
		for row in range(len(operators)):
			for col in range(len(operators)):
				if order_table[row][col] == '>' and f[row] <= g[col]:
					f[row] = g[col] + 1
					is_changed = 1
		for col in range(len(operators)):
			for row in range(len(operators)):
				if order_table[row][col] == '<' and f[row] >= g[col]:
					g[col] = f[row] + 1
					is_changed = 1
		for row in range(len(operators)):
			for col in range(len(operators)):
				if order_table[row][col] == '=' and f[row] != g[col]:
					f[row] = g[col] = max(f[row], g[col])
					is_changed = 1

	print "Precedence functions"
	print "F: {}".format(f)
	print "G: {}".format(g)

	## Analysis

	parse(f, g, operators, input_string)
	# stack = []

	# stack.append('$') 
	
	# print '{: <60}{: <60}{: <25}{: <10}'.format('Stack', 'Input', 'Precedence relation', 'Action')
	# vlaag = 1
	# # while vlaag:
	# for i in range(10):
	# 	if input_ind[0] == '$' and len(stack)==2:
	# 		vlaag = 0

	# 	length = len(input_ind)

	# 	buffer_inp = input_ind[0] 
	# 	temp1 = operators.index(str(buffer_inp))
	# 	# print "stack",stack, stack[-1]
	# 	if stack[-1] in non_terminals:
	# 		buffer_stack = stack[-2]
	# 	else:
	# 		buffer_stack = stack[-1]
	# 	temp2 = operators.index(str(buffer_stack))
	# 	#print buffer_inp, buffer_stack
					
	# 	# precedence = order_table[temp2][temp1]
	# 	# if precedence == '<':
	# 	# 	action = 'shift'
	# 	# elif precedence == '>':
	# 	# 	action = 'reduce'

	# 	if f[temp1] > g[temp2]:
	# 		action = 'shift'
	# 		precedence = '>'
	# 	elif f[temp1] < g[temp2]:
	# 		action = 'reduce'
	# 		precedence = '<'
	# 	else:
	# 		action = 'pass'
	# 		precedence = '='

				
	# 	print '{: <60}{: <60}{: ^25}{: <10}'.format(stack, input_ind, precedence, action)
		
	# 	if action == 'shift':
	# 		stack.append(buffer_inp)
	# 		input_ind.remove(buffer_inp)
	# 	elif action == 'reduce':
	# 		for key, value in master.iteritems():
	# 			var1 = ''.join(stack[-1:])
	# 			var2 = ''.join(stack[-3:])
	# 			if str(key) == str(buffer_stack):
	# 				stack[-1] = value
	# 				break
	# 			elif key == var1 or stack[-3:]==list(var1):
	# 				stack[-3:] = value
	# 				break
	# 			elif key == var2:
	# 				stack[-3:] = value	
	# 	else:
	# 		stack.append(buffer_inp)

	# 	del buffer_inp, temp1, buffer_stack, temp2, precedence
		
	# 	if vlaag == 0:
	# 		print "\nAccepted"
		
	# return 2
	
if __name__ == "__main__":
	sys.exit(main())




# ,+,-,*,/,i,(,),!,$
# +,>,>,<,<,<,<,>,>,>
# -,>,>,<,<,<,<,>,>,>
# *,>,>,>,>,<,<,>,>,>
# /,>,>,>,>,<,<,>,>,>
# i,>,>,>,>,,,>,>,>
# (,<,<,<,<,<,<,=,,>
# ),>,>,>,>,,,>,>,>
# !,<,<,<,<,<,<,,=,>
# $,<,<,<,<,<,<,<,<,


# A ->!B!
# B ->B+T
# T ->T*M
# M -> i
# |(B)
