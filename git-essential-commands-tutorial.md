---
title: "Git Essential Commands: A Complete Developer's Guide"
category: "Development"
subcategory: "Version Control"
tags: ["Git", "Version Control", "Development", "Programming", "Tutorial", "Commands", "GitHub", "Workflow"]
excerpt: "Master Git with this comprehensive guide covering essential commands, best practices, and real-world examples. From basic operations to advanced workflows, learn everything you need to become proficient with Git version control."
author: "Amstack Team"
date: "2026-01-21"
featured_image: "git-tutorial-cover.jpg"
reading_time: "12 min read"
difficulty: "Beginner to Intermediate"
---

# Git Essential Commands: A Complete Developer's Guide

Git is the backbone of modern software development, enabling teams to collaborate efficiently and track changes in their codebase. Whether you're a beginner or looking to refresh your knowledge, this comprehensive guide covers the most essential Git commands with practical examples.

## Table of Contents

1. [Getting Started with Git](#getting-started-with-git)
2. [Repository Setup](#repository-setup)
3. [Basic Git Workflow](#basic-git-workflow)
4. [Working with Files](#working-with-files)
5. [Staging and Committing](#staging-and-committing)
6. [Viewing History and Changes](#viewing-history-and-changes)
7. [Branch Management](#branch-management)
8. [Remote Repository Operations](#remote-repository-operations)
9. [Merging and Conflict Resolution](#merging-and-conflict-resolution)
10. [Undoing Changes](#undoing-changes)
11. [Advanced Commands](#advanced-commands)
12. [Git Best Practices](#git-best-practices)
13. [Common Git Workflows](#common-git-workflows)
14. [Troubleshooting](#troubleshooting)

---

## Getting Started with Git

### Initial Configuration

Before using Git, configure your identity and preferences:

```bash
# Set your name and email (required)
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

# Set default branch name
git config --global init.defaultBranch main

# Set default editor
git config --global core.editor "code --wait"  # For VS Code
git config --global core.editor "vim"          # For Vim

# View current configuration
git config --list

# View specific configuration
git config user.name
git config user.email
```

### Getting Help

```bash
# General help
git help

# Help for specific command
git help commit
git commit --help

# Short help
git commit -h
```

---

## Repository Setup

### Creating a New Repository

```bash
# Initialize a new Git repository
git init

# Initialize with specific branch name
git init --initial-branch=main
git init -b main

# Clone an existing repository
git clone https://github.com/username/repository.git

# Clone to specific directory
git clone https://github.com/username/repository.git my-project

# Clone specific branch
git clone -b develop https://github.com/username/repository.git
```

### Repository Information

```bash
# Check repository status
git status

# Short status format
git status -s

# Check remote repositories
git remote -v

# Add remote repository
git remote add origin https://github.com/username/repository.git

# Change remote URL
git remote set-url origin https://github.com/username/new-repository.git
```

---

## Basic Git Workflow

The typical Git workflow involves these steps:

1. **Modify** files in your working directory
2. **Stage** changes you want to include in the next commit
3. **Commit** staged changes to the repository
4. **Push** commits to remote repository

```bash
# Basic workflow example
git add .                    # Stage all changes
git commit -m "Add feature"  # Commit with message
git push origin main         # Push to remote
```

---

## Working with Files

### Adding Files to Staging Area

```bash
# Add specific file
git add filename.txt

# Add multiple files
git add file1.txt file2.txt file3.txt

# Add all files in directory
git add .

# Add all files (including deleted ones)
git add -A

# Add files by pattern
git add *.js
git add src/*.py

# Interactively add changes
git add -i

# Add parts of a file (patch mode)
git add -p filename.txt
```

### Removing Files

```bash
# Remove file from working directory and staging area
git rm filename.txt

# Remove file only from staging area (keep in working directory)
git rm --cached filename.txt

# Remove directory recursively
git rm -r directory/

# Force removal
git rm -f filename.txt
```

### Moving and Renaming Files

```bash
# Rename/move file
git mv oldname.txt newname.txt
git mv file.txt directory/

# This is equivalent to:
mv oldname.txt newname.txt
git rm oldname.txt
git add newname.txt
```

---

## Staging and Committing

### Committing Changes

```bash
# Commit with message
git commit -m "Your commit message"

# Commit with detailed message
git commit -m "Short description" -m "Longer description with more details"

# Add and commit in one step (tracked files only)
git commit -am "Add and commit message"

# Commit with editor for detailed message
git commit

# Amend last commit (change message or add files)
git commit --amend -m "New commit message"

# Amend without changing message
git commit --amend --no-edit
```

### Viewing Staged Changes

```bash
# Show staged changes
git diff --staged
git diff --cached

# Show unstaged changes
git diff

# Show changes for specific file
git diff filename.txt
```

---

## Viewing History and Changes

### Commit History

```bash
# View commit history
git log

# One line per commit
git log --oneline

# Show last n commits
git log -n 5
git log -5

# Show commits with file changes
git log --stat

# Show commits with actual changes
git log -p

# Graphical representation
git log --graph --oneline --all

# Filter by author
git log --author="John Doe"

# Filter by date
git log --since="2023-01-01"
git log --until="2023-12-31"
git log --since="2 weeks ago"

# Filter by commit message
git log --grep="bug fix"

# Show commits for specific file
git log -- filename.txt
```

### Viewing Specific Commits

```bash
# Show specific commit
git show commit-hash
git show HEAD
git show HEAD~1  # Previous commit

# Show files changed in commit
git show --name-only commit-hash

# Show only the commit message
git show --format="%s" --no-patch commit-hash
```

### Blame and Annotations

```bash
# Show who changed each line
git blame filename.txt

# Blame with line numbers
git blame -L 10,20 filename.txt

# Show file at specific revision
git show commit-hash:filename.txt
```

---

## Branch Management

### Creating and Switching Branches

```bash
# List branches
git branch          # Local branches
git branch -r       # Remote branches
git branch -a       # All branches

# Create new branch
git branch feature-branch

# Create and switch to new branch
git checkout -b feature-branch
git switch -c feature-branch  # Git 2.23+

# Switch to existing branch
git checkout main
git switch main  # Git 2.23+

# Switch to previous branch
git checkout -
git switch -
```

### Branch Operations

```bash
# Rename current branch
git branch -m new-branch-name

# Rename specific branch
git branch -m old-name new-name

# Delete local branch
git branch -d feature-branch

# Force delete branch
git branch -D feature-branch

# Delete remote branch
git push origin --delete feature-branch

# Track remote branch
git branch --set-upstream-to=origin/main main
```

---

## Remote Repository Operations

### Working with Remotes

```bash
# List remotes
git remote
git remote -v

# Add remote
git remote add upstream https://github.com/original/repository.git

# Remove remote
git remote remove origin

# Rename remote
git remote rename origin upstream
```

### Fetching and Pulling

```bash
# Fetch changes from remote
git fetch origin

# Fetch all remotes
git fetch --all

# Pull changes (fetch + merge)
git pull origin main

# Pull with rebase
git pull --rebase origin main

# Pull all branches
git pull --all
```

### Pushing Changes

```bash
# Push to remote branch
git push origin main

# Push new branch to remote
git push -u origin feature-branch
git push --set-upstream origin feature-branch

# Push all branches
git push --all

# Force push (use with caution!)
git push --force
git push --force-with-lease  # Safer option

# Push tags
git push origin --tags
```

---

## Merging and Conflict Resolution

### Merging Branches

```bash
# Merge branch into current branch
git merge feature-branch

# Merge with no fast-forward
git merge --no-ff feature-branch

# Merge with commit message
git merge -m "Merge feature branch" feature-branch

# Abort merge
git merge --abort
```

### Resolving Conflicts

When conflicts occur during merge:

```bash
# Check conflict status
git status

# Edit conflicted files manually, then:
git add conflicted-file.txt

# Continue merge
git commit

# Or use merge tools
git mergetool

# Configure merge tool
git config --global merge.tool vimdiff
```

### Rebasing

```bash
# Rebase current branch onto main
git rebase main

# Interactive rebase (last 3 commits)
git rebase -i HEAD~3

# Continue rebase after resolving conflicts
git rebase --continue

# Abort rebase
git rebase --abort

# Skip current commit during rebase
git rebase --skip
```

---

## Undoing Changes

### Unstaging Changes

```bash
# Unstage specific file
git reset HEAD filename.txt
git restore --staged filename.txt  # Git 2.23+

# Unstage all changes
git reset HEAD
```

### Discarding Changes

```bash
# Discard changes in working directory
git checkout -- filename.txt
git restore filename.txt  # Git 2.23+

# Discard all changes
git checkout -- .
git restore .

# Clean untracked files
git clean -f

# Clean untracked files and directories
git clean -fd

# Dry run (see what would be cleaned)
git clean -n
```

### Reverting Commits

```bash
# Revert specific commit (creates new commit)
git revert commit-hash

# Revert merge commit
git revert -m 1 merge-commit-hash

# Reset to previous commit (destructive)
git reset --hard HEAD~1

# Reset but keep changes in working directory
git reset --soft HEAD~1

# Reset and keep changes unstaged
git reset --mixed HEAD~1
```

---

## Advanced Commands

### Stashing Changes

```bash
# Stash current changes
git stash
git stash push -m "Work in progress"

# List stashes
git stash list

# Apply most recent stash
git stash pop
git stash apply

# Apply specific stash
git stash apply stash@{2}

# Drop stash
git stash drop stash@{1}

# Clear all stashes
git stash clear

# Stash including untracked files
git stash -u
```

### Cherry-picking

```bash
# Apply specific commit to current branch
git cherry-pick commit-hash

# Cherry-pick multiple commits
git cherry-pick commit1 commit2

# Cherry-pick a range
git cherry-pick commit1..commit2
```

### Tagging

```bash
# List tags
git tag

# Create lightweight tag
git tag v1.0.0

# Create annotated tag
git tag -a v1.0.0 -m "Version 1.0.0 release"

# Tag specific commit
git tag v1.0.0 commit-hash

# Push tags to remote
git push origin v1.0.0
git push origin --tags

# Delete tag
git tag -d v1.0.0
git push origin --delete v1.0.0
```

### Submodules

```bash
# Add submodule
git submodule add https://github.com/user/repo.git path/to/submodule

# Initialize submodules
git submodule init

# Update submodules
git submodule update

# Clone repository with submodules
git clone --recursive https://github.com/user/repo.git

# Update submodule to latest commit
git submodule update --remote
```

---

## Git Best Practices

### Commit Messages

Follow these conventions for clear commit messages:

```bash
# Good commit messages
git commit -m "Add user authentication feature"
git commit -m "Fix login validation bug"
git commit -m "Update documentation for API endpoints"

# Use conventional commits
git commit -m "feat: add user registration"
git commit -m "fix: resolve login timeout issue"
git commit -m "docs: update README with setup instructions"
```

### Branching Strategy

```bash
# Feature branch workflow
git checkout -b feature/user-auth
# ... make changes ...
git commit -m "Implement user authentication"
git push -u origin feature/user-auth
# ... create pull request ...
```

### .gitignore File

Create a `.gitignore` file to exclude files:

```gitignore
# Dependencies
node_modules/
venv/
*.pyc

# IDE files
.vscode/
.idea/

# OS files
.DS_Store
Thumbs.db

# Build output
dist/
build/
*.log
```

---

## Common Git Workflows

### Feature Branch Workflow

```bash
# 1. Start from main branch
git checkout main
git pull origin main

# 2. Create feature branch
git checkout -b feature/new-feature

# 3. Make changes and commit
git add .
git commit -m "Add new feature"

# 4. Push feature branch
git push -u origin feature/new-feature

# 5. Create pull request on GitHub/GitLab
# 6. After review, merge and cleanup
git checkout main
git pull origin main
git branch -d feature/new-feature
```

### Hotfix Workflow

```bash
# 1. Create hotfix branch from main
git checkout main
git pull origin main
git checkout -b hotfix/critical-bug

# 2. Fix the bug
git add .
git commit -m "Fix critical security bug"

# 3. Push and merge quickly
git push -u origin hotfix/critical-bug
# ... merge immediately ...

# 4. Tag the release
git tag -a v1.0.1 -m "Hotfix release"
git push origin v1.0.1
```

---

## Troubleshooting

### Common Issues and Solutions

**Problem: Merge conflicts**
```bash
# 1. Check which files have conflicts
git status

# 2. Edit files to resolve conflicts
# 3. Stage resolved files
git add .

# 4. Complete the merge
git commit
```

**Problem: Wrong commit message**
```bash
# Amend last commit message
git commit --amend -m "Correct message"
```

**Problem: Committed to wrong branch**
```bash
# Move last commit to different branch
git checkout correct-branch
git cherry-pick wrong-branch
git checkout wrong-branch
git reset --hard HEAD~1
```

**Problem: Need to undo last commit**
```bash
# Keep changes in working directory
git reset --soft HEAD~1

# Remove changes completely
git reset --hard HEAD~1
```

**Problem: Lost commits**
```bash
# Find lost commits
git reflog

# Recover lost commit
git checkout lost-commit-hash
git checkout -b recovery-branch
```

---

## Conclusion

Git is a powerful tool that becomes more intuitive with practice. Start with the basic commands and gradually incorporate more advanced features into your workflow. Remember these key points:

1. **Commit often** with meaningful messages
2. **Use branches** for features and experiments
3. **Keep your repository clean** with `.gitignore`
4. **Learn from mistakes** using Git's safety features
5. **Collaborate effectively** with remotes and pull requests

### Quick Reference Card

```bash
# Essential daily commands
git status          # Check repository status
git add .           # Stage all changes  
git commit -m ""    # Commit changes
git push            # Push to remote
git pull            # Pull from remote
git checkout -b     # Create new branch
git merge           # Merge branches
git log --oneline   # View commit history
```

Keep this guide handy as you develop your Git skills. The more you practice these commands, the more natural version control will become in your development workflow.

---

**Tags:** Git, Version Control, Development, Programming, Tutorial, Commands, GitHub, Workflow

**Related Articles:**
- Advanced Git Workflows for Teams
- Setting Up CI/CD with Git Hooks
- Git Security Best Practices
- Mastering GitHub Pull Requests