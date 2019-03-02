#!/usr/bin/env python3

debug_mode = 0

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

    class StackElem:
        def __init__(self, symbol, is_term, alt_idx=-1):
            self.symbol = symbol
            self.is_term = is_term
            self.alt_idx = alt_idx

        def __repr__(self):
            return "['{}'|{}|{}]".format(self.symbol, self.is_term, self.alt_idx)

    def parse(self, rules, expression):
        self.rules = rules
        self.input = expression
        self.input_index = 0


        self.__normalize_rules()
        self.__init_alternatives()

        self.first_stack = []
        self.second_stack = []

        self.root_symbol = 'B'
        self.second_stack.append(Parser.StackElem(self.root_symbol, False))

        self.state = "ok"

        i = 0
        while True:
            print("\nIteration #{}: state = {}".format(i, self.state)) if debug_mode else None
            self.__print_stack()

            if self.state == "ok":
                self.__process()
            elif self.state == "ret":
                self.__ret()
            elif self.state == "exit":
                return self.__exit()
            i += 1

    def __is_term(self, symbol):
        return not symbol in self.rules.left

    def __print_stack(self):
        if debug_mode:
            print("first_stack: {}".format(self.first_stack))
            print("second_stack: {}".format(self.second_stack))
            print("input: {}".format(self.input))
            print("       " + " " * self.input_index + "^")

    def __get_alternative(self, symbol, n):
        for alternative in self.alternatives:
            if alternative.symbol == symbol and n < alternative.count:
                return self.rules.right[alternative.first_pos + n]
        return None

    def __push_alternative(self, symbol, n):
        for symbol in self.__get_alternative(symbol, n)[::-1]:
            first_elem = Parser.StackElem(symbol, self.__is_term(symbol))
            self.second_stack = [first_elem] + self.second_stack

    def __init_alternatives(self):
        self.alternatives = []
        for char in list(set(self.rules.left)):
            first_pos = self.rules.left.find(char)
            count = self.rules.left.count(char)
            self.alternatives.append(
                Parser.Alternative(char, first_pos, count))

    def __normalize_rules(self):
        sorted_rules = sorted(zip(self.rules.left, self.rules.right))
        self.rules.left = ""
        self.rules.right = []
        for elem in sorted_rules:
            self.rules.left += elem[0]
            self.rules.right.append(elem[1])

    def __process(self):
        active_head = self.second_stack[0]
        if active_head.is_term:
            if active_head.symbol == self.input[self.input_index]:
                print("step 2") if debug_mode else None
                self.first_stack.append(
                    Parser.StackElem(active_head.symbol, True))
                self.second_stack = self.second_stack[1:]
                self.input_index += 1

                need_ret = False
                if self.input_index == len(self.input):
                    if not self.second_stack:
                        print("step 3") if debug_mode else None
                        self.result = True
                        self.state = "exit"
                    else:
                        need_ret = True
                elif not self.second_stack:
                        need_ret = True
                if need_ret:
                    print("step 3'") if debug_mode else None
                    self.state = "ret"
            else:
                print("step 4") if debug_mode else None
                self.state = "ret"
        else:
            print("step 1") if debug_mode else None
            self.first_stack.append(
                Parser.StackElem(active_head.symbol, False, 0))

            self.second_stack = self.second_stack[1:]
            for symbol in self.__get_alternative(active_head.symbol, 0)[::-1]:
                first_elem = Parser.StackElem(symbol, self.__is_term(symbol))
                self.second_stack = [first_elem] + self.second_stack

    def __ret(self):
        active_head = self.first_stack[-1]
        if active_head.is_term:
            print("step 5") if debug_mode else None
            first_elem = Parser.StackElem(active_head.symbol, True)
            self.second_stack = [first_elem] + self.second_stack
            self.first_stack = self.first_stack[:-1]
            self.input_index -= 1
        elif self.__get_alternative(active_head.symbol, active_head.alt_idx + 1):
            print("step 6a") if debug_mode else None
            alt_len = len(self.__get_alternative(
                active_head.symbol, active_head.alt_idx))
            self.second_stack = self.second_stack[alt_len:]
            active_head.alt_idx += 1
            self.__push_alternative(active_head.symbol, active_head.alt_idx)
            self.state = "ok"
        elif active_head.symbol == self.root_symbol:  # and self.input_index == 0:
            print("step 6b") if debug_mode else None
            self.result = False
            self.state = "exit"
        else:
            print("step 6B") if debug_mode else None
            alt_len = len(self.__get_alternative(
                active_head.symbol, active_head.alt_idx))
            self.second_stack = self.second_stack[alt_len:]

            first_elem = Parser.StackElem(active_head.symbol, False)
            self.second_stack = [first_elem] + self.second_stack
            self.first_stack = self.first_stack[:-1]

    def __exit(self):
        print("\nExpression for test: '{}'".format(self.input))
        print("Root symbol: {}".format(self.root_symbol))
        print("Grammar rules:")
        for i in range(len(self.rules.left)):
            print("    {n}) '{left}' -> '{right}'".format(n=i+1,
                                                          left=self.rules.left[i], right=self.rules.right[i]))
        if self.result:
            print("Result: good")
            print("Inference: [ ", end='')
            inference = []
            for elem in self.first_stack:
                if not elem.is_term:
                    first_entry = self.rules.left.find(elem.symbol)
                    inference.append(first_entry + elem.alt_idx + 1)
                    print(inference[-1], end=' ')
            print("]")
            return True, inference
        else:
            print("Result: bad")
            return False

expression1 = "a+b+a+b*a*b+a*b"
rules1 = Parser.Rules("BBTTMM", ["T+B", "T", "M", "M*T", "a", "b"])

expression2 = "!a+((b*a)*(a+(b)))!"
rules2 = Parser.Rules(
    "BAATTMMM", ["!A!", "T+A", "T", "M", "M*T", "a", "b", "(A)"])

parser = Parser()
parser.parse(rules1, expression1)

parser = Parser()
parser.parse(rules2, expression2)
