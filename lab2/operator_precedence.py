import sys
import shlex
import csv

class operator_precedence_parser:
	def __init__(self, grammar_filename, matrix_filename):
		self.__read_grammar(grammar_filename)
		self.__read_precedence_matrix(matrix_filename)
		self.__generate_precedence_functions()

	def __read_input(self, input_filename):
		input_string = open(input_filename, 'r')
		input_string = input_string.read()
		self.input_ind = list(shlex.shlex(input_string))
		print('Input: {}\n'.format(input_string))

	def __read_grammar(self, grammar_filename):
		self.rules = {}
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
				self.rules[master_list[x][y]] = self.non_terminals[x]

		for key, value in self.rules.iteritems():
			if '->' in key:
				length = len(key)
				for i in range(length):
					if key[i] == '-' and key[i + 1] == ">":
						index = i+2
						break
				var_key = key
				new_key = key[index:]

				var = self.rules[var_key]
				del self.rules[var_key]
				self.rules[new_key] = var

		print('Rules: {}'.format(self.rules))
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

	def __get_order(self, lhs, rhs):
		return self.order_table[self.operators.index(lhs)][self.operators.index(rhs)]

	def parse(self, input_filename):
		self.__read_input(input_filename)

		stack = []

		stack.append(self.input_ind[0])

		print('{: <60}{: <110}{: <25}'.format('Stack', 'Input', 'Precedence relation'))


		pointerStr = 1
		while pointerStr < len(self.input_ind):
			elemForStack = self.input_ind[pointerStr]

			# check whether the last character is a terminal in stack
			pointerStack = stack.__len__() - 1
			if stack[pointerStack] in self.non_terminals:
				pointerStack -= 1

			# find the ratio of the precedence
			# if self.__get_f(stack[pointerStack]) < self.__get_g(elemForStack):
			order = self.__get_order(stack[pointerStack], elemForStack)
			if order == '<':
				if pointerStack == (len(stack) - 1):
					stack.append('<')
					stack.append(elemForStack)
				else:
					tmp = stack.pop()
					stack.append('<')
					stack.append(tmp)
					stack.append(elemForStack)

			elif order == '>':
				lastElemStack = stack.pop()
				while lastElemStack[-1:] != '<':
					lastElemStack += stack.pop()

				lastElemStack = lastElemStack[:-1]
				lastElemStack = lastElemStack[::-1]

				for key, value in self.rules.iteritems():
					if key == lastElemStack:
						lastElemStack = value
						pointerStr -= 1
						break
				
				stack.append(lastElemStack)

			elif order == '=':
				stack.append(elemForStack)
			else:
				print('This input not in this grammatic!')
				return

			print('{: <60}{: <110}{: ^25}'.format(
				stack, self.input_ind[pointerStr:], order))
			pointerStr += 1


		result = ''
		for ch in stack:
			result += ch
		print(result)

		for key, value in self.rules.iteritems():
			if key == result:
				result = value

		if result == self.start_state:
			print('Correct')
		else:
			print('Incorrect')

	
def main():
	parser = operator_precedence_parser(
		grammar_filename='grammar1.txt',
		matrix_filename='order2.csv'
	)
	parser.parse(
		input_filename='input1.txt'
	)
	return 2
	
if __name__ == "__main__":
	sys.exit(main())
