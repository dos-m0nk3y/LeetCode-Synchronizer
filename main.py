import os
import time
import json
import pathlib
import requests
import datetime
import email.utils
import urllib.parse
from git import Repo
import leetcode_query


def parse_git_log():
    commits = dict()
    for commit in Repo(os.getcwd()).iter_commits():
        if commit.message not in commits:
            commits[commit.message] = int(commit.committed_datetime.timestamp())

    return commits


def scrape_leetcode():
    session = requests.Session()
    session.cookies.set("LEETCODE_SESSION", os.environ.get("LEETCODE_SESSION"), domain="leetcode.com")
    session.cookies.set("csrftoken", os.environ.get("LEETCODE_CSRF_TOKEN"), domain="leetcode.com")

    solved_problems = list()
    all_problems = session.get("https://leetcode.com/api/problems/all/").json()
    for problem in all_problems["stat_status_pairs"]:
        if problem["status"] == "ac":
            time.sleep(1)

            title_slug = problem["stat"]["question__title_slug"]
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36",
                "Connection": "keep-alive",
                "Content-Type": "application/json",
                "Referer": "https://leetcode.com/problems/" + title_slug,
            }

            json_data = leetcode_query.question_detail
            json_data["variables"]["titleSlug"] = title_slug
            question_details = session.post("https://leetcode.com/graphql", json=json_data, headers=headers, timeout=10).json()

            json_data = leetcode_query.submission_list
            json_data["variables"]["questionSlug"] = title_slug
            submissions = session.post("https://leetcode.com/graphql", json=json_data, headers=headers, timeout=10).json()

            json_data = leetcode_query.submission_details
            json_data["variables"]["submissionId"] = submissions["data"]["questionSubmissionList"]["submissions"][0]["id"]
            submission_details = session.post("https://leetcode.com/graphql", json=json_data, headers=headers, timeout=10).json()

            problem_info = {
                "id": int(problem["stat"]["frontend_question_id"]),
                "title": problem["stat"]["question__title"],
                "title_slug": title_slug,
                "content": question_details["data"]["question"]["content"],
                "difficulty": question_details["data"]["question"]["difficulty"],
                "skills": [tag["name"] for tag in question_details["data"]["question"]["topicTags"]],
                "timestamp": int(submissions["data"]["questionSubmissionList"]["submissions"][0]["timestamp"]),
                "language": submissions["data"]["questionSubmissionList"]["submissions"][0]["langName"],
                "code": submission_details["data"]["submissionDetails"]["code"],
            }
            solved_problems.append(problem_info)

    return sorted(solved_problems, key=lambda entry: entry["timestamp"])


def sync_github(commits, submissions):
    repo = Repo(os.getcwd())
    url = urllib.parse.urlparse(repo.remote("origin").url)
    url = url._replace(netloc=f"{os.environ.get('GITHUB_TOKEN')}@" + url.netloc)
    url = url._replace(path=url.path + ".git")
    repo.remote("origin").set_url(url.geturl())

    commit = list(repo.iter_commits())[0]
    repo.config_writer().set_value("user", "name", commit.author.name).release()
    repo.config_writer().set_value("user", "email", commit.author.email).release()

    for submission in submissions:
        commit_message = f"Sync LeetCode Submission - {submission['title']} ({submission['language']})"
        if commit_message not in commits or commits[commit_message] < submission["timestamp"]:
            dir_name = f"{str(submission['id']).zfill(4)}-{submission['title_slug']}"
            if submission["language"] == "C++":
                ext = "cpp"
            elif submission["language"] == "MySQL":
                ext = "sql"
            elif submission["language"] == "Bash":
                ext = "sh"
            else:
                raise Exception(f"Unknown language : {submission['language']}")

            pathlib.Path(f"problems/{dir_name}").mkdir(parents=True, exist_ok=True)
            with open(f"problems/{dir_name}/{dir_name}.{ext}", "wt") as fd:
                fd.write(submission["code"].strip())
            with open(f"problems/{dir_name}/README.md", "wt") as fd:
                content = f"<h2>{submission['id']}. {submission['title']}</h2>\n\n"
                content += submission["content"].strip()
                fd.write(content)

            # RFC 2822 (Thu, 07 Apr 2005 22:13:13 +0200) / ISO 8601 (2005-04-07T22:13:13)
            # https://github.com/gitpython-developers/GitPython/blob/master/git/objects/util.py#L134
            iso_datetime = email.utils.format_datetime(datetime.datetime.fromtimestamp(submission["timestamp"]))
            os.environ["GIT_AUTHOR_DATE"] = iso_datetime
            os.environ["GIT_COMMITTER_DATE"] = iso_datetime
            repo.index.add("**")
            repo.index.commit(commit_message)
            repo.git.push("origin")
            os.unsetenv("GIT_AUTHOR_DATE")
            os.unsetenv("GIT_COMMITTER_DATE")

            new_submission = {"id": submission["id"], "title": submission["title"], "difficulty": submission["difficulty"], "skills": submission["skills"]}

            saved_submissions = list()
            if os.path.isfile("submissions.json"):
                with open("submissions.json", "rt") as fd:
                    saved_submissions = json.load(fd)

            if new_submission not in saved_submissions:
                saved_submissions.append(new_submission)
                # update_readme(saved_submissions)
                with open("submissions.json", "wt") as fd:
                    json.dump(saved_submissions, fd, ensure_ascii=False, indent=2)


def main():
    commits = parse_git_log()
    submissions = scrape_leetcode()
    sync_github(commits, submissions)


if __name__ == "__main__":
    main()
