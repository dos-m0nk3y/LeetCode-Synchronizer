question_detail = {
    "query": """
            query getQuestionDetail($titleSlug: String!) {
                question(titleSlug: $titleSlug) {
                    content
                    difficulty
                    topicTags {
                        name
                        slug
                    }
                }
            }
        """,
    "variables": {"titleSlug": ""},
    "operationName": "getQuestionDetail",
}

submission_list = {
    "query": """
            query submissionList($offset: Int!, $limit: Int!, $questionSlug: String!) {
                questionSubmissionList(
                    offset: $offset
                    limit: $limit
                    questionSlug: $questionSlug
                ) {
                    submissions {
                        id
                        langName
                        timestamp
                    }
                }
            }
        """,
    "variables": {"questionSlug": "", "offset": 0, "limit": 1},
    "operationName": "submissionList",
}

submission_details = {
    "query": """
        query submissionDetails($submissionId: Int!) {
            submissionDetails(submissionId: $submissionId) {
                code
            }
        }
    """,
    "variables": {"submissionId": ""},
    "operationName": "submissionDetails",
}
