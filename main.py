from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse
from pathlib import Path


import get_data
import get_specificdata

app = FastAPI()

templates = Jinja2Templates(directory="templates")

result = get_data.get_spaces()
lis_spaces = []
for space in result:
    space_name = space['name']
    space_key = space['key']
    mapped_spaces = {'name': space_name, 'value': space_key}
    lis_spaces.append(mapped_spaces)
# Sample list of spaces
spaces = lis_spaces

@app.get("/", response_class=HTMLResponse)
async def read_main():
    # Return the HTML page
    return HTMLResponse(content=open("templates/index.html").read(), status_code=200)

@app.get("/list_spaces", response_class=JSONResponse)
async def list_spaces():
    # Return the list of spaces as JSON
    return JSONResponse(content=spaces, status_code=200)


# @app.get("/space_validation")
# async def space_validation(space):
#     print('started')
#     matched_data = get_data.process_space(space)
#     print('file completed')
#     return FileResponse(matched_data, headers={"Content-Disposition": "attachment; filename=test_sample.xlsx"})

global_matched_data = None
global_file_name = None

@app.get("/space_validation", response_class=JSONResponse)
async def space_validation(space):
    print('started')
    global global_matched_data
    global_matched_data = get_data.process_space(space)
    global global_file_name
    global_file_name = [f'{space}_mattchedData.xlsx', f'{space}_missingData.xlsx']
    print('file completed')
    if global_matched_data[2]:
        message = f'''found attachment discrepancy from {space}
                    for details we can find in {global_file_name[1]}'''
    if global_matched_data[2]:
        message = f'''found pages discrepancy from {space}
                    for details we can find in {global_file_name[1]}'''
    if not (global_matched_data[2] and global_matched_data[2]):
        message = f'''No discrepancy found from {space}
                    for details we can find in {global_file_name[0]}'''

    return JSONResponse(content={"file_name": global_file_name, "message": message}, status_code=200)

@app.get("/download_matchedfile")
async def space_download():
    print('downloading_file')
    
    return FileResponse(global_matched_data[0], headers={"Content-Disposition": f"attachment; filename={global_file_name[0]}"})

@app.get("/download_missingfile")
async def space_download():
    print('downloading_file')
    
    return FileResponse(global_matched_data[1], headers={"Content-Disposition": f"attachment; filename={global_file_name[1]}"})


@app.get("/get_pagetitles", response_class=HTMLResponse)
async def space_pagetitles(request: Request, space):
    mapped_pageids = get_specificdata.get_target_pages(space)
    # return JSONResponse(content=mapped_pageids, status_code=200)
    return templates.TemplateResponse("title.html", {"request": request, "page_titles": mapped_pageids})

@app.get("/get_pageattachments", response_class=JSONResponse)
async def page_attachments(page_id):
    page_attachments = get_specificdata.validate_attachements(page_id)
    print(page_attachments)
    return JSONResponse(content=page_attachments, status_code=200)

@app.get("/get_pagecomments", response_class=JSONResponse)
async def page_comments(page_id):
    page_comments = get_specificdata.get_page_comments(page_id)
    print(page_comments)
    return JSONResponse(content=page_comments, status_code=200)

@app.get("/get_brokenurls", response_class=JSONResponse)
async def page_brokenurls(page_id, broken_urls=True):
    page_brokenurls = get_specificdata.extract_urls_from_page_content(
                        page_id, broken_urls)
    print(page_brokenurls)
    return JSONResponse(content=page_brokenurls, status_code=200)

@app.get("/get_listurls", response_class=JSONResponse)
async def page_listurls(page_id, broken_urls=False):
    page_listurls = get_specificdata.extract_urls_from_page_content(
                        page_id, broken_urls)
    print(page_listurls)
    return JSONResponse(content=page_listurls, status_code=200)

