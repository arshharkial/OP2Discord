import requests
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import json
import io

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/webhook/")
async def get_type(request: Request):
    # TODO Add get webhook functionality
    webhook = await request.body()
    webhook = json.load(io.BytesIO(webhook))
    print(webhook)
    content: str = ""
    state: str = ""
    embedTitle: str = ""
    embedContent: str = ""
    title: str = ""
    color: str = "11119017"
    url: str = ""

    discord_webhook: str = ""

    if webhook.get("action") in ["work_package:created", "work_package:updated"]:
        work_package = webhook.get("work_package", {})
        embedTitle = work_package.get("subject")
        state = work_package.get("_embedded", {}).get("status", {}).get("name", "")
        content: str = "**Work Package**\n"
        embedContent: str = ""
        url: str = (
            f"https://openproject.devkraft.in/work_packages/{work_package.get('id')}"
        )
        color = "11119017"  # Grey
        if state == "In progress":
            color = "16766720"  # Yellow
        elif state == "Closed":
            color = "32768"  # Green
        elif state == "On hold":
            color = "15438417"  # Orange

        if work_package.get("_embedded", {}).get("project", "").get("name", ""):
            project_name = (
                work_package.get(
                    "_embedded",
                    {},
                )
                .get(
                    "project",
                    "",
                )
                .get(
                    "name",
                    "",
                )
            )
            content += f"Project: **{project_name}**\n"
        if work_package.get("dueDate", ""):
            content += f"Due Date: **{work_package.get('dueDate', '')}**\n"
        if work_package.get("updatedAt", ""):
            content += f"Updated At: **{work_package.get('updatedAt', '')}**\n"
        if work_package.get("description").get("raw", ""):
            embedContent = work_package.get("description").get("raw", "")[:150]
        if work_package.get("_embedded", {}).get("author").get("name", ""):
            updated_by = (
                work_package.get(
                    "_embedded",
                    {},
                )
                .get(
                    "author",
                )
                .get(
                    "name",
                    "",
                )
            )
            content += f"Updated By: **{updated_by}**\n"
        if work_package.get("_embedded", {}).get("responsible", {}).get("name", ""):
            responsible = (
                work_package.get(
                    "_embedded",
                    {},
                )
                .get(
                    "responsible",
                )
                .get(
                    "name",
                    "",
                )
            )
            content += f"Assigned To: **{responsible}**\n"
        if work_package.get("_embedded", {}).get("assignee", {}).get("name", ""):
            assignee = (
                work_package.get(
                    "_embedded",
                    {},
                )
                .get(
                    "assignee",
                )
                .get(
                    "name",
                    "",
                )
            )
            content += f"Assigned By: **{assignee}**\n"
        title = f"{state} | {embedTitle}"

    elif webhook.get("action") in ["attachment:created"]:
        content: str = "**Attachment Uploaded**\n"
        attachment = webhook.get("attachment")
        embedContent = attachment.get("description", {}).get("raw", "")
        url: str = f"https://openproject.devkraft.in/work_packages/{attachment.get('_embedded', {}).get('container').get('id')}"
        if attachment.get("fileName", ""):
            content += f"Filename: **{attachment.get('fileName', '')}**\nWork package: **{attachment.get('_embedded', {}).get('container').get('subject')}**\n"
            title = attachment.get("fileName", "")
        if attachment.get("_embedded", {}).get("author").get("name", ""):
            updated_by = (
                attachment.get(
                    "_embedded",
                    {},
                )
                .get(
                    "author",
                    {},
                )
                .get(
                    "name",
                    "",
                )
            )
            content += f"Uploaded By: **{updated_by}**\n"

    elif webhook.get("action") in ["project:updated", "project:created"]:
        content: str = "**Project**\n"
        project = webhook.get("project")
        content += f"Project Name: **{project.get('name', '')}**\nUpdated At: **{project.get('updatedAt', '')}**"
        title = project.get("name", "")
        embedContent = project.get("description", "").get("raw", "")[:150]
        url = f"https://openproject.devkraft.in/projects/{project.get('identifier', 0)}"

    elif webhook.get("action") in ["time_entry:created"]:
        content: str = "**Time Log**\n"
        time_entry = webhook.get("time_entry")
        title = "Time Entry"
        embedContent = ""
        url = f"https://openproject.devkraft.in/work_packages/{time_entry.get('_embedded', {}).get('workPackage').get('id')}"
        content += f"Project: **{time_entry.get('_embedded', {}).get('project', {}).get('name', '')}**\nWork Package: **{time_entry.get('_embedded', {}).get('workPackage', {}).get('subject', '')}**\nUser: **{time_entry.get('_embedded', {}).get('user', '').get('name', '')}**\nActivity: **{time_entry.get('_embedded', {}).get('activity').get('name', '')}**\nComments: **{time_entry.get('comment', {}).get('raw')[:50]}**\nTime: **{time_entry.get('hours', '')}**\nDate: **{time_entry.get('spentOn', '')}**"

    data = {
        "username": "ArcaBot",
        "content": content,
        "embeds": [
            {
                "title": title,
                "description": embedContent,
                "color": color,
                "url": url,
            }
        ],
    }

    headers = {"Content-Type": "application/json"}

    result = requests.post(discord_webhook, json=data, headers=headers)

    if 200 <= result.status_code < 300:
        print(f"Webhook sent {result.status_code}")
    else:
        print(
            f"Not sent with {result.status_code}, response:\n{result.json()}",
        )

    return {}


def main() -> None:
    uvicorn.run(app, port=8080, host="0.0.0.0")


if __name__ == "__main__":
    main()
