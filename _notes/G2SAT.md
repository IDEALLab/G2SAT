**Live notes as I learn to understand the paper.**

- [1. Basics of SAT (Wiki)](#1-basics-of-sat-wiki)
  - [1.1 Definition and terminology](#11-definition-and-terminology)
  - [1.2 The Boolean Satisfiability Problem (SAT)](#12-the-boolean-satisfiability-problem-sat)

# 1. Basics of SAT ([Wiki](https://en.wikipedia.org/wiki/Boolean_satisfiability_problem))

## 1.1 Definition and terminology

1. A **boolean expression/propositional logic formula** is bulit from:
   - Variables: `x_1`, `x_2`.
   - Conjunctions: AND, `∧`.
   - Disjunctions: OR, `∨`.
   - Negations: NOT, `¬`.
   - Parentheses: `(` `)`.

2. A **literal** could be a positive literal (正文字) `x`, or a negative literal (反文字) `¬x`.
   
   A **clause (子句)** is a disjuntion `∨` of literals (or a single literal). 用**或**连接。 
  
3. A formula is in **Conjunctive Normal Form (CNF)** if it is a conjunction `∧` of clauses (or a single clause). 用**与**连接。
   
   For example, `(x1 ∨ ¬x2) ∧ (¬x1 ∨ x2 ∨ x3) ∧ ¬x1` consists of 3 clauses.
   
   > Using the laws of Boolean algebra, every propositional logic formula can be transformed into an equivalent conjunctive normal form, which may, however, be exponentially longer.

## 1.2 The Boolean Satisfiability Problem (SAT)
1. SAT is the problem to determine whether a formula is satisfiable or not.
   
   A boolean formula is called "**satisfiable**" if there **exists** a set of `TRUE` or `FALSE` values assigned to each variable such that this formula is `True`. If no such assignment exists, then this formula is called "**unsatisfiable**".
   
   For example, by choosing `x1` = `FALSE`, `x2` = `FALSE`, and `x3` arbitrarily, the above formula is `TRUE`. So it is satisfiable. 

2. SAT is the first problem that was proven to be NP-complete.

3. In the form of CNF, each clause must be `TRUE`.

4. > As of 2007, heuristic SAT-algorithms are able to solve problem instances involving tens of thousands of variables and formulas consisting of millions of symbols, which is sufficient for many practical SAT problems from, e.g., artificial intelligence, **circuit design**, and automatic theorem proving.




