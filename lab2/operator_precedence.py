import sys
import shlex
import csv

class operator_precedence_parser:
	def __init__(self, grammar_filename, matrix_filename):
		self.__read_grammar(grammar_filename)
		self.__read_precedence_matrix(matrix_filename)
		self.__generate_precedence_functions()

	def __read_input(self, input_filename):
		# input_string = "i + i - i"
		input_string = open(input_filename, 'r')
		input_string = input_string.read()
		self.input_ind = list(shlex.shlex(input_string))
		# self.input_ind.append('$')
		print('Input: {}\n'.format(input_string))

	def __read_grammar(self, grammar_filename):
		self.master = {}
		self.non_terminals = []
		self.start_state = ''
		master_list = []
		new_list = []

		grammar = open(grammar_filename, 'r')

		for row2 in grammar:
			if '->' in row2:
				#new production
				if len(new_list) == 0:
					self.start_state = row2[0]
					self.non_terminals.append(row2[0])
					new_list = []
					new_list.append(row2.rstrip('\n'))
				else:
					master_list.append(new_list)
					del new_list
					new_list = []
					new_list.append(row2.rstrip('\n'))
					self.non_terminals.append(row2[0])
			elif '|' in row2:
				new_list.append(row2.rstrip('\n'))

		master_list.append(new_list)
		for x in range(len(master_list)):
			for y in range(len(master_list[x])):
				master_list[x][y] = [s.replace('|', '') for s in master_list[x][y]]
				master_list[x][y] = ''.join(master_list[x][y])
				self.master[master_list[x][y]] = self.non_terminals[x]

		for key, value in self.master.iteritems():
			if '->' in key:
				length = len(key)
				for i in range(length):
					if key[i] == '-' and key[i + 1] == ">":
						index = i+2
						break
				var_key = key
				new_key = key[index:]

				var = self.master[var_key]
				del self.master[var_key]
				self.master[new_key] = var

		print('Rules: {}'.format(self.master))
		print('Start state: {}'.format(self.start_state))
		print('Non terms: {}'.format(self.non_terminals))

	def __read_precedence_matrix(self, matrix_filename):
		self.order_table = []
		with open(matrix_filename, 'rU') as file2:
			order = csv.reader(file2)
			for row in order:
				self.order_table.append(row)
		
		self.operators = self.order_table[0]

		print("Precedence matrix:")
		print('\n'.join(['\t'.join([str(cell) for cell in row]) for row in self.order_table]) + '\n')

	def __generate_precedence_functions(self):
		self.f = [1] * len(self.operators)
		self.g = [1] * len(self.operators)

		is_changed = 1
		while is_changed:
			is_changed = 0
			for row in range(len(self.operators)):
				for col in range(len(self.operators)):
					if self.order_table[row][col] == '>' and self.f[row] <= self.g[col]:
						self.f[row] = self.g[col] + 1
						is_changed = 1
			for col in range(len(self.operators)):
				for row in range(len(self.operators)):
					if self.order_table[row][col] == '<' and self.f[row] >= self.g[col]:
						self.g[col] = self.f[row] + 1
						is_changed = 1
			for row in range(len(self.operators)):
				for col in range(len(self.operators)):
					if self.order_table[row][col] == '=' and self.f[row] != self.g[col]:
						self.f[row] = self.g[col] = max(self.f[row], self.g[col])
						is_changed = 1

		print("Precedence functions:")
		print("F: {}".format(self.f))
		print("G: {}\n".format(self.g))

	def __get_f(self, ch):
		return self.f[self.operators.index(ch)]

	def __get_g(self, ch):
		return self.g[self.operators.index(ch)]

	def parse(self, input_filename):
		self.__read_input(input_filename)

		stack = []

		stack.append(self.input_ind[0])

		print('{: <60}{: <60}{: <25}{: <10}'.format('Stack', 'Input', 'Precedence relation', 'Action'))
		vlaag = 1
		while vlaag:
		# for i in range(10):
			if self.input_ind[0] == '$' and len(stack) == 2:
				vlaag = 0

			length = len(self.input_ind)

			buffer_inp = self.input_ind[0]
			temp1 = self.operators.index(str(buffer_inp))
			# print "stack",stack, stack[-1]
			if stack[-1] in self.non_terminals:
				buffer_stack = stack[-2]
			else:
				buffer_stack = stack[-1]
			temp2 = self.operators.index(str(buffer_stack))
			#print buffer_inp, buffer_stack

			# precedence = self.order_table[temp2][temp1]
			# if precedence == '<':
			# 	action = 'shift'
			# elif precedence == '>':
			# 	action = 'reduce'

			if self.f[temp1] > self.g[temp2]:
				action = 'shift'
				precedence = '>'
			elif self.f[temp1] < self.g[temp2]:
				action = 'reduce'
				precedence = '<'
			else:
				action = 'pass'
				precedence = '='

			print('{: <60}{: <60}{: ^25}{: <10}'.format(stack, self.input_ind, precedence, action))

			if action == 'shift':
				stack.append(buffer_inp)
				self.input_ind.remove(buffer_inp)
			elif action == 'reduce':
				for key, value in self.master.iteritems():
					var1 = ''.join(stack[-1:])
					var2 = ''.join(stack[-3:])
					if str(key) == str(buffer_stack):
						stack[-1] = value
						break
					elif key == var1 or stack[-3:] == list(var1):
						stack[-3:] = value
						break
					elif key == var2:
						stack[-3:] = value
			else:
				stack.append(buffer_inp)

			del buffer_inp, temp1, buffer_stack, temp2, precedence

			if vlaag == 0:
				print("\nAccepted")

	def parse2(self, input_filename):
		self.__read_input(input_filename)

		# PARSING = ''
		# POLIZE = ''
		stack = []
		# mop = MOP()

		# START
		stack.append(self.input_ind[0])

		pointerStr = 1
		while pointerStr < len(self.input_ind):
			# elemInStr = self.input_ind[pointerStr]
			elemForStack = self.input_ind[pointerStr]

			# # check the self.input_ind and replace the identifier with 'I'
			# if elemInStr in TERM:
			# 	elemForStack = elemInStr
			# elif elemInStr in IDENT:
			# 	# POLIZE += elemInStr
			# 	# PARSING += '4' # ???!!!
			# 	elemForStack = 'I'
			# else:
			# 	assert(print('ERROR in main(): incorrect input data!'))

			# check whether the last character is a terminal in stack
			pointerStack = stack.__len__() - 1
			if stack[pointerStack] in self.non_terminals:
				pointerStack -= 1
				# check that the penultimate character in the stack is a terminal
				# if stack[pointerStack] not in TERM:
					# assert(print("ERROR in main(): the penultimate character in the stack isn't a terminal"))
					# print("ERROR in main(): the penultimate character in the stack isn't a terminal")

			# find the ratio of the precedence
			# if mop.get((stack[pointerStack], elemForStack)) == '<':
			if self.__get_f(stack[pointerStack]) < self.__get_g(elemForStack):
				if pointerStack == (len(stack) - 1):
					stack.append('<')
					stack.append(elemForStack)
				else:
					tmp = stack.pop()
					stack.append('<')
					stack.append(tmp)
					stack.append(elemForStack)
			# elif mop.get((stack[pointerStack], elemForStack)) == '>':
			elif self.__get_f(stack[pointerStack]) > self.__get_g(elemForStack):

				lastElemStack = stack.pop()
				while lastElemStack[-1:] != '<':
					lastElemStack += stack.pop()

				lastElemStack = lastElemStack[:-1]
				lastElemStack = lastElemStack[::-1]

				# Among the generating rules, we seek a rule containing the primary phrase on the right-hand side of
				# strForRules = ''
				# for ch in lastElemStack:
				# 	if ch == 'i':
				# 		strForRules += 'NONTERM'
				# 	elif ch in self.non_terminals:
				# 		strForRules += 'NONTERM'
					# elif ch in TERM:
					# else:
					# 	strForRules += ch
					# else:
						# assert(print("ERROR in main(): incorrect variable : lastElemStack"))
						# print("ERROR in main(): incorrect variable : lastElemStack")

				# for print rules
				# for rules in RULES_RESOLVER:
				# 	for rightRules in RULES_RESOLVER[rules]:
				# 		if rightRules == strForRules:
				# 			# PARSING += str(First_PLACE_in_RULES_RESOLVER[rules])
				# 			# try:
				# 				# POLIZE += For_Polize[rules]
				# 			# except:
				# 			# 	pass
				# 			break

				# for next steps
				# for rules in RULES:
				# 	for rightRules in RULES[rules]:
				# 		if rightRules == lastElemStack:
				# 			lastElemStack = rules
				# 			pointerStr -= 1
				# 			break
				for key, value in self.master.iteritems():
					if key == lastElemStack:
						lastElemStack = value
						pointerStr -= 1
						break

				stack.append(lastElemStack)
			# elif mop.get((stack[pointerStack], elemForStack)) == '=':
			elif self.__get_f(stack[pointerStack]) == self.__get_g(elemForStack):
				stack.append(elemForStack)
			else:
				print('This input not in this grammatic!')
				return

			pointerStr += 1
			print(stack)

		result = ''
		for ch in stack:
			result += ch
		print(result)


		# for rules in RULES:
		# 	for rightRules in RULES[rules]:
		# 		if rightRules == result:
		# 			result = rules
		# 			# PARSING += '1'

		if result == self.start_state:
			# print(PARSING)
			# print(POLIZE)
			print('Correct')
		else:
			print('Incorrect')

	
def main():
	parser = operator_precedence_parser(
		grammar_filename='grammar1.txt',
		matrix_filename='order2.csv'
	)
	parser.parse2(
		input_filename='input1.txt'
	)
	return 2
	
if __name__ == "__main__":
	sys.exit(main())
