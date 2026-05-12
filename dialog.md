# Defining a "Stable" Checkpoint in Git

In Git, there are two primary ways to mark your current code as a stable checkpoint so you can easily revert to it later if things break: **Tags** and **Branches**.

Here is how you use both to protect your functional code.

---

## Method 1: Git Tags (The "Bookmark" Approach)

A Git Tag is exactly what it sounds like—a sticky note attached to a specific commit. It is the standard way to mark milestones, versions, or releases. Unlike branches, tags don't move when you make new commits; they permanently point to the exact state of the files at that moment in time.

### How to create a Tag:
Right now, you are at a stable point (v2.3.0). To tag it:
```bash
# Create an annotated tag (-a) with a message (-m)
git tag -a v2.3.0 -m "Stable release: Phased pipeline with audio extraction"

# If you use a remote repository (like GitHub), push the tag to the server:
git push origin v2.3.0
```

### How to use the Tag later:
If you start building speaker diarization tomorrow and everything completely breaks, you can instantly look at or revert to your tagged version.

**To simply look around at the stable code without overwriting your current work:**
```bash
git checkout v2.3.0
```

**To completely wipe away your broken changes and hard-reset your project back to the stable tag:**
```bash
# WARNING: This deletes any uncommitted changes!
git reset --hard v2.3.0
```

---

## Method 2: Git Branches (The "Parallel Universe" Approach)

While Tags are great for marking the past, Branches are the best way to protect the present while building the future. Instead of building the risky new Diarization feature on top of your stable code, you create an isolated copy (a branch).

### How to use Branches:
Assuming your current stable code is on the `main` branch.

1. **Create a safe sandbox for the new feature:**
   ```bash
   # Create and switch to a new branch called "feature/diarization"
   git checkout -b feature/diarization
   ```

2. **Work normally:**
   You edit files, break things, and make commits. None of this affects the `main` branch.

3. **If things go horribly wrong (The Revert):**
   You realize the diarization code is a mess and you want your stable code back. You just switch back to `main` and delete the failed experiment:
   ```bash
   git checkout main
   git branch -D feature/diarization
   ```

4. **If things go perfectly (The Merge):**
   The new feature works! You switch back to your stable branch and merge the new code in, updating your stable checkpoint.
   ```bash
   git checkout main
   git merge feature/diarization
   ```

---

## Summary Recommendation

For the best workflow:
1. Make sure all your current stable code is committed to `main`.
2. Run `git tag -a v2.3.0 -m "Stable pipeline"` to permanently bookmark this moment.
3. Run `git checkout -b feature/speaker-mapping` to start working on the new speaker diarization features safely.
