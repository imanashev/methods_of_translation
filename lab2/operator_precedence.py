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
		self.input_ind.append('$')

	def __read_grammar(self, grammar_filename):
		self.master = {}
		self.master_list = []
		self.new_list = []
		self.non_terminals = []

		grammar = open(grammar_filename, 'r')

		for row2 in grammar:
			if '->' in row2:
				#new production
				if len(self.new_list) == 0:
					start_state = row2[0]
					self.non_terminals.append(row2[0])
					self.new_list = []
					self.new_list.append(row2.rstrip('\n'))
				else:
					self.master_list.append(self.new_list)
					del self.new_list
					self.new_list = []
					self.new_list.append(row2.rstrip('\n'))
					self.non_terminals.append(row2[0])
			elif '|' in row2:
				self.new_list.append(row2.rstrip('\n'))

		self.master_list.append(self.new_list)
		for x in xrange(len(self.master_list)):
			for y in xrange(len(self.master_list[x])):
				self.master_list[x][y] = [s.replace('|', '') for s in self.master_list[x][y]]
				self.master_list[x][y] = ''.join(self.master_list[x][y])
				self.master[self.master_list[x][y]] = self.non_terminals[x]

		for key, value in self.master.iteritems():
			if '->' in key:
				length = len(key)
				for i in xrange(length):
					if key[i] == '-' and key[i + 1] == ">":
						index = i+2
						break
				var_key = key
				new_key = key[index:]

		var = self.master[var_key]
		del self.master[var_key]
		self.master[new_key] = var

	def __read_precedence_matrix(self, matrix_filename):
		self.order_table = []
		with open(matrix_filename, 'rU') as file2:
			order = csv.reader(file2)
			for row in order:
				self.order_table.append(row)
		
		self.operators = self.order_table[0]

		print "Precedence matrix"
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

		print "Precedence functions"
		print "F: {}".format(self.f)
		print "G: {}\n".format(self.g)

	def parse(self, input_filename):
		self.__read_input(input_filename)

		stack = []

		stack.append('$')

		print '{: <60}{: <60}{: <25}{: <10}'.format('Stack', 'Input', 'Precedence relation', 'Action')
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

			print '{: <60}{: <60}{: ^25}{: <10}'.format(stack, self.input_ind, precedence, action)

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
				print "\nAccepted"


	
def main():
	parser = operator_precedence_parser(
		grammar_filename='grammar.txt',
		matrix_filename='order.csv'
	)
	parser.parse(
		input_filename='input.txt'
	)
	return 2
	
if __name__ == "__main__":
	sys.exit(main())
