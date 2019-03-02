#!/usr/bin/env python3

debug_mode = 1

class Parser:
    class Rules:
        def __init__(self, left, right):
            self.left = left
            self.right = right

    class Alternative:
        def __init__(self, symbol, first_pos, count):
            self.symbol = symbol
            self.first_pos = first_pos
            self.count = count

    class First_stack_elem:
        def __init__(self, symbol, is_term, alt_idx = -1):
            self.symbol = symbol
            self.is_term = is_term
            self.alt_idx = alt_idx

        def __repr__(self):
            return "['{}'|{}|{}]".format(self.symbol, self.is_term, self.alt_idx)

    class Second_stack_elem:
        def __init__(self, symbol, is_term):
            self.symbol = symbol
            self.is_term = is_term

        def __repr__(self):
            return "['{}'|{}]".format(self.symbol, self.is_term)

    def is_term(self, symbol):
        return not symbol in self.rules.left

    def debug(self):
        if debug_mode:
            print("first_stack: {}".format(self.first_stack))
            print("second_stack: {}".format(self.second_stack))
            print("input: {}".format(self.input))
            print("       " + " " * self.input_index + "^")

    def get_alternative(self, symbol, n):
        for alternative in self.alternatives:
            if alternative.symbol == symbol and n < alternative.count:
                return self.rules.right[alternative.first_pos + n]
        # print("Alternative for '{}' #{} not found".format(symbol,n))
        return None

    def push_alternative(self, symbol, n):
        for symbol in self.get_alternative(symbol, n)[::-1]:
            first_elem = Parser.Second_stack_elem(symbol, self.is_term(symbol))
            self.second_stack = [first_elem] + self.second_stack

    def init_alternatives(self):
        self.alternatives = []
        for char in list(set(self.rules.left)):
            first_pos = self.rules.left.find(char)
            count = self.rules.left.count(char)
            self.alternatives.append(Parser.Alternative(char, first_pos, count))

    def normalize_rules(self):
        sorted_rules = sorted(zip(self.rules.left, self.rules.right))
        self.rules.left = ""
        self.rules.right = []
        for elem in sorted_rules:
            self.rules.left += elem[0]
            self.rules.right.append(elem[1])

    def parse(self, rules, expression):
        self.rules = rules
        self.input = expression

        self.normalize_rules()
        self.init_alternatives()
        self.root_symbol = 'B'
        self.first_stack = []
        self.second_stack = []
        self.second_stack.append(Parser.Second_stack_elem(self.root_symbol, False))

        self.input_index = 0
        self.state = "ok"

        i = 0
        while True:
            if debug_mode: print("\niteration #{}: state = {}".format(i, self.state))
            self.debug()

            if self.state == "ok":
                self.__process()
            elif self.state == "ret":
                self.__ret()
            elif self.state == "exit":
                self.__exit()
                return
            i += 1

    def __ret(self):
        active_head = self.first_stack[-1]
        if active_head.is_term:
            if debug_mode: print("step 5")
            first_elem = Parser.Second_stack_elem(active_head.symbol, True)
            self.second_stack = [first_elem] + self.second_stack
            self.first_stack = self.first_stack[:-1]
            self.input_index -= 1
        elif self.get_alternative(active_head.symbol, active_head.alt_idx + 1):
            if debug_mode: print("step 6a")
            alt_len = len(self.get_alternative(active_head.symbol, active_head.alt_idx))
            self.second_stack = self.second_stack[alt_len:]
            active_head.alt_idx += 1
            self.push_alternative(active_head.symbol, active_head.alt_idx)
            self.state = "ok"
        elif active_head.symbol == self.root_symbol:# and self.input_index == 0:
            if debug_mode: print("step 6b")
            self.result = False
            self.state = "exit"
        else:
            if debug_mode: print("step 6B")
            alt_len = len(self.get_alternative(active_head.symbol, active_head.alt_idx))
            self.second_stack = self.second_stack[alt_len:]
            
            first_elem = Parser.Second_stack_elem(active_head.symbol, False)
            self.second_stack = [first_elem] + self.second_stack
            self.first_stack = self.first_stack[:-1]
        
    def __exit(self):
        print("\nExpression for test: '{}'".format(self.input))
        print("Root symbol: {}".format(self.root_symbol))
        print("Grammar rules:")
        for i in range(len(self.rules.left)):
            print("    {n}) '{left}' -> '{right}'".format(n=i+1, left=self.rules.left[i], right=self.rules.right[i]))
        if self.result:
            print("Result: good")
            print("Inference: [ ", end='')
            for elem in self.first_stack:
                if not elem.is_term:
                    first_entry = self.rules.left.find(elem.symbol)
                    print(first_entry + elem.alt_idx + 1, end=' ')
            print("]")
        else:
            print("Result: bad")

    def __process(self):
        active_head = self.second_stack[0]
        if active_head.is_term:
            if active_head.symbol == self.input[self.input_index]:
                if debug_mode: print("step 2")
                self.first_stack.append(Parser.First_stack_elem(active_head.symbol, True))
                self.second_stack = self.second_stack[1:]
                self.input_index += 1

                need_ret = False
                if self.input_index == len(self.input):
                    if not self.second_stack:
                        if debug_mode: print("step 3")
                        self.result = True
                        self.state = "exit"
                    else:
                        need_ret = True
                elif not self.second_stack:
                        need_ret = True
                if need_ret:
                    if debug_mode: print("step 3'")
                    self.state = "ret"
            else:
                if debug_mode: print("step 4")
                self.state = "ret" 
        else:
            if debug_mode: print("step 1")
            self.first_stack.append(Parser.First_stack_elem(active_head.symbol, False, 0))

            self.second_stack = self.second_stack[1:]
            for symbol in self.get_alternative(active_head.symbol, 0)[::-1]:
                first_elem = Parser.Second_stack_elem(symbol, self.is_term(symbol))
                self.second_stack = [first_elem] + self.second_stack
            

expression1 = "a+b"
rules1 = Parser.Rules("BBTTMM", ["T+B", "T", "M", "M*T", "a", "b"])

expression2 = "!a+b!"
rules2 = Parser.Rules("BAATTMMM", ["!A!", "T+A", "T", "M", "M*T", "a", "b", "(A)"])

parser = Parser()
parser.parse(rules2,expression2)
