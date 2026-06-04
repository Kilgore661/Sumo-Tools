Understood. The scenario is:

**You:**

> Help me with `https://github.com/Kilgore661/Sumo-Tools/tree/dev`.
> Starting from `dev`, create a branch called `chatgpt/syntax-fix` and fix the syntax errors in `src/.../foo.py`. Do not change `dev`.

**Me:**

> Done. I created `chatgpt/syntax-fix` from `dev` and committed the fix there. `dev` is unchanged.

**You, on `X:`:**

```powershell
cd X:\path\to\Sumo-Tools
git fetch origin
git diff origin/dev...origin/chatgpt/syntax-fix
```

Review the change in your GUI.

When approved:

```powershell
git switch dev
git merge origin/chatgpt/syntax-fix
git push origin dev
```

Done.

What happens to syntax-fix after the change has been accepted and pushed, and
I want another change?

You, after accepting the first change:

git switch dev
git merge origin/chatgpt/syntax-fix
git push origin dev
git push origin --delete chatgpt/syntax-fix

---

To see what has changed:

`git fetch origin dev`

`git diff --name-status HEAD..origin/dev`

To get the changes without conflicts:

`git pull --ff-only`
