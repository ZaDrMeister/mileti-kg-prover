# Research diary

One short entry for every day you work on the project. It takes 10 minutes at the end of a session.

**Why bother:**
- **Interviews.** "Why did you encode →I that way?" Your diary has the answer and the date.
- **The paper.** Decisions and surprises written down now become the method and discussion sections later.
- **Letters.** Send CCB (or a future advisor) a link or a weekly summary; it shows steady, independent work.
- **Momentum.** The "Next step" line tells you exactly where to start tomorrow.

## How to add an entry

From the project folder:
```bash
./diary/new-entry.sh
```
This creates `diary/entries/YYYY-MM-DD.md` from the template below and prints its path. (Running it twice on the same day just prints the existing file.) Then fill it in and commit:
```bash
git add diary && git commit -m "Diary: YYYY-MM-DD" && git push
```

## Rules for yourself
1. **Write it the same day.** Short is fine; skipped is not.
2. **Facts first.** What you did, with the evidence: a commit, a number, an error message.
3. **Record decisions with a reason.** "Atoms are Nat *because* …"
4. **Record confusion.** "I don't understand why →I needs the *last* assumption" is a useful entry. Mark it ❓ and mark it ✅ when it's resolved.
5. **Be honest about AI help.** Note what Claude or another tool did (explained an error, reviewed code, wrote harness code). This keeps your "what I did myself" claims accurate.

**Privacy:** this folder is in the **public** repo. Don't write anything private here (grades, health, other people). If you'd rather keep the diary private, add `diary/entries/` to `.gitignore`.

## Weekly review (every Sunday, 15 min)
Add a `## Week review` section to your Sunday entry:
- What moved forward this week (with commits)?
- What's blocked, and what would unblock it?
- Are you on track for the current milestone (`docs/MILESTONES.md`)?
- One sentence you could send to your supervisor.

## Template
The script copies `diary/TEMPLATE.md`. Edit that file to change the template.
