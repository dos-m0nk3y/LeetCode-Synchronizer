# LeetCode Synchronizer

**LeetCode Synchronizer** is a GitHub Action that automatically collects and organizes LeetCode submissions into a GitHub repository.

Here's a sample repository created using LeetCode Synchronizer: [leetcode-synchronizer-sample](https://github.com/dos-m0nk3y/leetcode-synchronizer-sample)

## Features

- Fully automated collection of all your latest accepted submissions with minimal effort setup
- Single commit for each submission stamped with the original submission date for building rich and accurate contributions graph
- Automated git pushes to the remote repository with every action triggers

## Setup

1. Retrieve LeetCode cookies

   - Login to LeetCode
   - Open `Web Developer Tools`
   - Find `https://leetcode.com` from `Storage > Cookies`
   - Copy values for cookies `LEETCODE_SESSION` and `csrftoken`

2. Create a GitHub repository for LeetCode synchronization

3. Create [GitHub Secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets) for LeetCode API access

   - Open `Settings > Secrets and variables > Actions` from the repository
   - Click `New repository secret`
   - Create a new secret `LEETCODE_SESSION` using `LEETCODE_SESSION` cookie value
   - Create a new secret `LEETCODE_CSRF_TOKEN` using `csrftoken` cookie value

4. Give workflows write permissions in the repository for git pushes

   - Open `Settings > Actions > General` from the repository
   - Select `Read and write permissions` from `Workflow permissions` and save

5. Create [GithHub Action](https://docs.github.com/en/actions/quickstart)

   - Create a workflow directory `.github/workflows/`
   - Create a workflow file, e.g., `leetcode_synchronizer.yml`
   - Copy the following YAML contents into the `leetcode_synchronizer.yml` file:

     ```yml
     name: LeetCode Synchronizer
     on: workflow_dispatch
     jobs:
       build:
         runs-on: ubuntu-latest
         steps:
           - name: Run LeetCode Synchronizer
             uses: dos-m0nk3y/LeetCode-Synchronizer@v1.0.0
             with:
               GITHUB_TOKEN: ${{ github.token }}
               LEETCODE_SESSION: ${{ secrets.LEETCODE_SESSION }}
               LEETCODE_CSRF_TOKEN: ${{ secrets.LEETCODE_CSRF_TOKEN }}
     ```

6. Trigger GitHub action

   - Open `Actions > LeetCode Synchronizer` from the repository
   - Click `Run workflow > Run workflow`

## Inputs

- `GITHUB_TOKEN` - **required**. GitHub token used in pushing submissions to the repository
- `LEETCODE_SESSION` - **required**. LeetCode session used in accessing LeetCode API
- `LEETCODE_CSRF_TOKEN` - **required**. LeetCode CSRF token used in accessing LeetCode API
