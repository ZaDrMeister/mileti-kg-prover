# Step 1, for beginners: Mileti's formulas in Lean

This guide assumes **you have never used Lean**. By the end you will have:

- written `lean/MiletiLogic/Syntax.lean` yourself: Mileti's propositional formulas as a Lean type, with notation and two recursive functions;
- checked it with Lean;
- made your first commit;
- written your first research-diary entry.

**Total time:** about 4–6 hours, and it's fine to split it over 2–3 days. Each part says roughly how long it takes.

**The one rule:** *you* write everything in `Syntax.lean`. This guide teaches with **other** examples (colors, shapes, arithmetic) that you then translate to formulas. When you're stuck, ask Claude what an error *means*, or for a hint. Don't ask for the code. Interviewers will ask you about this file.

Every Lean snippet in this guide was compiled with your Lean version (v4.28.0) on 2026-11-25. If one fails for you, the problem is in your setup or a typo, not the snippet.

---

## Part 0. What you're building, and why (10 min, just read)

In Mileti, a **formula** is built from:
- **atoms** (propositional symbols like A, B, C), and
- **connectives** that build bigger formulas from smaller ones: ¬φ, φ∧ψ, φ∨ψ, φ→ψ.

Mileti gets this from a **generating system**: start with the atoms and keep applying the connectives. He writes formulas as strings in Polish notation (`∧AB` means A∧B), so he has to *prove* that every formula can be read in only one way (unique readability).

In Lean you describe formulas as a **tree** instead:

```
        →                 this tree is   (A ∧ B) → (A ∨ B)
      /   \
     ∧     ∨
    / \   / \
   A   B A   B
```

Lean's `inductive` keyword creates exactly this kind of tree type. Lean *guarantees* that each tree is built in only one way, which is the unique-readability property for free. Keep that in mind; it's the first "aha" of the project.

Everything else in the project sits on this type: the deduction rules (step 2), the gates (Python), and the Lean check of every proof. So step 1 is small but important.

---

## Part 1. One-time setup (20–30 min)

### 1.1 Check that Lean works
Open Terminal and run:
```bash
cd ~/Desktop/grad-school-project/mileti-kg-prover/lean
~/.elan/bin/lake build
```
✅ You should see `Build completed successfully`. If you don't, stop and ask Claude, pasting the whole output.

### 1.2 Set up VS Code for Lean
1. Open VS Code. The `code` command is already installed on your Mac.
2. Go to Extensions (⇧⌘X), search **lean4**, and install the one by **leanprover**.
3. **File → Open Folder…** and choose `~/Desktop/grad-school-project/mileti-kg-prover/lean`. Open the `lean` folder itself, not the whole project, so the extension finds `lakefile.lean`.
4. Open `MiletiLogic/Syntax.lean`. Wait a few seconds; a status bar at the bottom shows Lean starting.
5. Open the **infoview**: ⇧⌘P → type `Lean 4: Infoview: Toggle`. A panel opens on the right. That's where Lean "talks" to you: results, errors and goals.

### 1.3 Make a scratch file for practice
Create `lean/Scratch.lean` (File → New File, save it in the `lean` folder). You'll practise there. It's **not** part of the project; `.gitignore` already contains `lean/Scratch.lean`, so git ignores it.
Test it by typing into Scratch.lean:
```lean
#eval 2 + 3
```
Put your cursor on that line. ✅ The infoview should show `5`. If it does, your setup works.

---

## Part 2. A Lean crash course in 5 mini-lessons (1.5–2 hours)

Type every example yourself; don't paste. Typing is how the syntax sticks. Unicode tip: in VS Code with the Lean extension, type `\to` + space for →, `\and` for ∧, `\or` for ∨, `\not` for ¬, `\ne` for ≠, `\phi` for φ.

### Lesson A: values, functions, checks
```lean
#eval 2 + 3                       -- runs code: shows 5
#eval "hello " ++ "Lean"          -- shows "hello Lean"

def double (n : Nat) : Nat := n + n
#eval double 21                   -- 42
#check double                     -- shows its type: double (n : Nat) : Nat

example : double 2 = 4 := by rfl  -- a tiny proof: Lean computes both sides and compares
```
What's new:
- `def name (input : Type) : OutputType := body` defines a function. `Nat` means natural numbers 0, 1, 2, …
- `#eval` **runs** something and `#check` **shows its type**.
- `example : statement := by rfl` asks Lean to **check** a fact by computing (`rfl` = "reflexivity", meaning both sides compute to the same thing). If the fact is false, you get a red error.
- `--` starts a comment.

**Try it:** write `def triple`, then an `example` showing `triple 3 = 9`. Then change it to `= 10` and read the error.

### Lesson B: your first `inductive` type (a list of options)
```lean
inductive Color where
  | red
  | green
  | blue
  deriving Repr, DecidableEq

#eval Color.red                                 -- Color.red
example : Color.red ≠ Color.blue := by decide   -- Lean decides it automatically

def Color.next : Color → Color
  | .red   => .green
  | .green => .blue
  | .blue  => .red

#eval Color.red.next                            -- Color.green
```
What's new:
- `inductive Color where` + lines starting with `|` lists the **constructors**, the only ways to make a `Color`.
- `deriving Repr` lets `#eval` *print* a Color. `deriving DecidableEq` lets Lean *decide* whether two Colors are equal. **You'll need both for formulas.**
- A function on an inductive type uses **pattern matching**: one line per constructor (`| .red => …`). The `.red` shorthand works because Lean knows the input is a Color.

**Try it:** add a fourth color, `yellow`. Lean now shows an error in `Color.next`. Read it: it says `Missing cases`. Fix it. This is Lean making sure you handled every case, which will protect you later.

### Lesson C: constructors that carry data
```lean
inductive Shape where
  | circle : Nat → Shape            -- a circle needs one number (radius)
  | rect   : Nat → Nat → Shape      -- a rectangle needs two numbers
  deriving Repr, DecidableEq

#eval Shape.rect 2 3                -- Shape.rect 2 3

def Shape.area : Shape → Nat
  | .circle r => 3 * r * r          -- names the data inside: r
  | .rect w h => w * h

#eval (Shape.rect 2 3).area         -- 6
```
What's new:
- `circle : Nat → Shape` reads as: "give me a Nat and I give you a Shape."
- `rect : Nat → Nat → Shape` means "give me two Nats and I give you a Shape."
- When matching, you **name** the data inside (`r`, `w`, `h`) and use it.

**Connect to Mileti:** an **atom** is like `circle`: a constructor that carries a *name* (a number or a string), not another formula.

### Lesson D: a type that contains itself (a tree), the key lesson
This is exactly the shape you need for formulas, but for arithmetic instead:
```lean
namespace Demo

inductive Expr where
  | num   : Nat → Expr               -- base case: like an atom
  | neg   : Expr → Expr              -- one smaller Expr inside: like ¬
  | plus  : Expr → Expr → Expr       -- two smaller Exprs: like ∧, ∨, →
  | times : Expr → Expr → Expr
  deriving DecidableEq, Repr

open Expr      -- lets you write `num 1` instead of `Expr.num 1`

-- size: count the nodes of the tree
def size : Expr → Nat
  | num _     => 1                   -- _ means "some data I don't need"
  | neg e     => size e + 1          -- calls itself on the smaller piece: RECURSION
  | plus a b  => size a + size b + 1
  | times a b => size a + size b + 1

-- height: the longest path from the top down
def height : Expr → Nat
  | num _     => 0
  | neg e     => height e + 1
  | plus a b  => max (height a) (height b) + 1
  | times a b => max (height a) (height b) + 1

-- subexprs: list every piece of the tree, including the whole tree
def subexprs : Expr → List Expr
  | num n     => [num n]
  | neg e     => neg e :: subexprs e                          -- :: puts one item at the front of a list
  | plus a b  => plus a b :: (subexprs a ++ subexprs b)       -- ++ joins two lists
  | times a b => times a b :: (subexprs a ++ subexprs b)

#eval size (plus (num 1) (neg (num 2)))       -- 4
#eval height (plus (num 1) (neg (num 2)))     -- 2
#eval subexprs (plus (num 1) (num 1))         -- [plus .., num 1, num 1]  (num 1 appears twice)
#eval (subexprs (plus (num 1) (num 1))).eraseDups   -- duplicates removed

example : plus (num 1) (num 2) ≠ plus (num 2) (num 1) := by decide

end Demo
```
What's new:
- `neg : Expr → Expr` means a constructor can take **another Expr**. That's what makes it a tree.
- Functions on trees **call themselves** on the smaller parts (recursion). Lean accepts this because the parts really are smaller (structural recursion), the same as Mileti's definitions by recursion on formulas.
- `namespace Demo … end Demo` keeps the names grouped (`Demo.Expr`). Your file uses `namespace MiletiLogic`.

**Try it:**
1. Write `countNums : Expr → Nat`, which counts only the `num` leaves. Check it with `#eval`.
2. Is `subexprs` a **list** or a **set**? It can contain duplicates. Mileti talks about the *set* of subformulas. Write in a comment which one you'll match, and why. (You can use `.eraseDups` to get set-like behaviour.)

### Lesson E: notation (writing trees like math)
```lean
-- (inside namespace Demo, after `open Expr`)
prefix:75 "−" => Expr.neg
infixl:65 " ⊕ " => Expr.plus
infixl:70 " ⊗ " => Expr.times      -- 70 > 65, so ⊗ binds tighter than ⊕

#eval num 1 ⊕ num 2 ⊗ num 3        -- plus (num 1) (times (num 2) (num 3))
example : (num 1 ⊕ num 2 ⊗ num 3) = plus (num 1) (times (num 2) (num 3)) := by rfl
example : (−num 1 ⊗ num 2) = times (neg (num 1)) (num 2) := by rfl
```
And how `infixr` (group to the right) works:
```lean
namespace R
inductive T where
  | leaf : Nat → T
  | arr  : T → T → T
  deriving Repr, DecidableEq
infixr:25 " ⇒ " => T.arr
open T
example : (leaf 1 ⇒ leaf 2 ⇒ leaf 3) = arr (leaf 1) (arr (leaf 2) (leaf 3)) := by rfl
end R
```
What's new:
- `prefix:N "sym" => f`: write `sym x` for `f x`.
- `infixl:N` / `infixr:N "sym" => f`: write `a sym b` for `f a b`. With several in a row, `infixl` groups from the left and `infixr` from the right.
- **Higher N binds tighter.** These `example … := by rfl` lines are how you *test* that your notation parses the way you intend.
- Pick symbols that aren't already used by Lean. Lean already uses `¬ ∧ ∨ →` for its *own* logic, so for your formulas choose different ones. For example, `∼ ⋀ ⋁ ⟶` work (tested); type them as `\sim`, `\bigwedge`, `\bigvee`, `\longrightarrow`. If Lean says `unexpected token`, the symbol is taken or clashes.

---

## Part 3. Read Mileti with a purpose (45 min)

Read **Ch. 2** (generating systems, especially "freely generated") and **§3.1** (the definition of formulas). Keep a page of notes, answering:

1. **Which connectives are primitive** in §3.1? (The design assumes ¬, ∧, ∨, →. Check it: is ↔ a primitive or an abbreviation? Is there ⊥?) Write your answer in your diary; only primitives become constructors.
2. **What are the atoms?** A set `P` of symbols. Does Mileti fix it or allow any set? (This affects whether you index atoms by `Nat` or by names.)
3. **How does Mileti define subformulas and depth/height?** Note the definition and section number; your Lean functions should match it.
4. **In your own words: why is an inductive type a free generating system?** Hint: (a) different constructors never produce the same tree, and (b) each constructor is one-to-one. Those are Mileti's freeness conditions.

Question 4 is excellent material for your statement of purpose ("formalizing the book made me see why unique readability matters…"). Write the answer in full sentences.

---

## Part 4. Build `Syntax.lean` (1.5–2 hours), one small step at a time

Open `lean/MiletiLogic/Syntax.lean`. Keep the checklist comment at the top and tick items as you go (`[x]`). Write code **between** `namespace MiletiLogic` and `end MiletiLogic`.

After **every** step: save, look at the infoview (no red), and run `~/.elan/bin/lake build` in Terminal.

### Step 4.1: Decide how atoms are named (10 min)
Two options:

| Option | Atom looks like | Good | Bad |
|---|---|---|---|
| `Nat` | `atom 0`, `atom 1` | Simplest; easy to generate many atoms | Python uses `A`, `B`, so the export needs a mapping (A→0, B→1, …) |
| `String` | `atom "A"` | Matches the Python harness directly | Slightly clunkier to write |

Choose one, and **write a comment explaining why**. Both are fine; the reason matters more than the choice.

### Step 4.2: Write `inductive Formula` (20 min)
Using Lesson D as your model:
- one constructor for **atoms** (carries a `Nat` or `String`, like `num`);
- one for **¬** (carries one `Formula`, like `neg`);
- one each for **∧, ∨, →** (carry two `Formula`s, like `plus`);
- `deriving DecidableEq, Repr`.

Name the constructors clearly (e.g. `atom`, `not`, `and`, `or`, `imp`). Add a comment pointing to Mileti's section.

✅ **Check:** add `#eval` lines building (A∧B)→(A∨B) *without* notation (e.g. `Formula.imp (…) (…)`). The infoview prints the tree. Also add:
```lean
example : <atom 0 or "A"> ≠ <atom 1 or "B"> := by decide   -- fill in with YOUR constructor
```
**Commit now** (Part 6 explains how). Your first commit is a milestone.

### Step 4.3: Notation (30 min)
Following Lesson E:
- choose a symbol and precedence for each connective;
- match the Python harness's order, so the same text means the same formula on both sides: **¬ binds tightest, then ∧, then ∨, then → loosest**, and **→ groups to the right** (`infixr`).

✅ **Check:** write one `example … := by rfl` for each of these:
1. `¬A ∧ B` is `(¬A) ∧ B`, not `¬(A ∧ B)`.
2. `A ∧ B ∨ C` is `(A ∧ B) ∨ C`.
3. `A → B → C` is `A → (B → C)`.

Each `example` compares your notation to the constructor form, as in Lesson E. If one fails, your precedence numbers are wrong. Good: the test caught it.

### Step 4.4: `subformulas` (20 min)
Write `subformulas : Formula → List Formula`, modelled on `subexprs`, matching Mileti's definition from Part 3.

✅ **Check:** for φ = (A∧B)→(A∨B), work out the subformulas **on paper first**, then `#eval` and compare. Decide about duplicates (A appears twice) and write your decision in a comment.

### Step 4.5: `depth` (15 min)
Write `depth : Formula → Nat`, modelled on `height`, matching Mileti's definition. Is an atom depth 0 or 1 in the book? Follow the book.

✅ **Check:** compute by hand and confirm with `example … := by rfl` for an atom, `¬A`, and (A∧B)→(A∨B).

### Step 4.6: Clean up (15 min)
- [ ] The comment at the top lists what's in the file, with Mileti references.
- [ ] Your Part 3, question 4 answer is in a comment (or in your diary).
- [ ] There's no `sorry` anywhere (`sorry` means "unfinished" in Lean).
- [ ] `lake build` passes with no errors.

---

## Part 5. "Done" checklist for step 1

- [ ] `Formula` with atoms and ¬ ∧ ∨ →, `deriving DecidableEq, Repr`
- [ ] Atom choice explained in a comment
- [ ] Notation with three passing precedence `example`s
- [ ] `subformulas` and `depth`, each checked by hand against 2–3 formulas
- [ ] At least one `≠ … := by decide` example
- [ ] `lake build` passes, no `sorry`
- [ ] Committed and pushed
- [ ] Diary entry written

---

## Part 6. Commit and push (5 min each time)

From the project folder:
```bash
cd ~/Desktop/grad-school-project/mileti-kg-prover
git status                                  # see what changed
git add lean/MiletiLogic/Syntax.lean
git commit -m "Syntax: Formula type with atoms and ¬ ∧ ∨ →"
git push
```
Write messages that say *what* you did. Commit after each step in Part 4, not just at the end. Many small commits are visible evidence of your own work on GitHub.

---

## Part 7. When something goes wrong

These are real Lean messages:

| You see | It means | Fix |
|---|---|---|
| `Missing cases: C.b` | A function doesn't handle every constructor | Add a line for the missing one |
| `failed to synthesize Decidable (…)` | Lean can't decide equality | Add `deriving DecidableEq` to the type |
| `Unknown identifier 'atom'` | The name isn't in scope | Write `Formula.atom`, or add `open Formula` |
| `unexpected token` at your symbol | The symbol is already used or clashes | Pick a different symbol |
| An `example … := by rfl` fails | The two sides aren't the same tree | Your notation precedence, or your hand calculation, is wrong |
| The infoview shows nothing | Lean is still starting, or you opened the wrong folder | Wait; make sure you opened the `lean` folder |

To ask Claude for help, paste: the code, the **full** error, and what you expected. Ask "what does this mean?" or "give me a hint", not "fix it".

Good references:
- *Theorem Proving in Lean 4*, chapters "Inductive Types" and "Induction and Recursion" (lean-lang.org).
- *Functional Programming in Lean* (lean-lang.org): very beginner-friendly for `def`, `inductive` and pattern matching.

---

## Part 8. After you finish

1. Write today's **diary entry** (see `diary/README.md`). Include what you decided (atoms, symbols, list vs set) and *why*.
2. Next is **step 2** (`Deduction.lean`): `inductive Derivable : List Formula → Formula → Prop`, one constructor per rule from `docs/design.md` §3. It uses the same `inductive` idea as `Formula`, but the type describes *what can be proved* instead of formulas. A separate guide will come when you're ready.
