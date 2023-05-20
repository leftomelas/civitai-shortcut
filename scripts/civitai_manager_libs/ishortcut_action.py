import os
import json
import gradio as gr
import datetime
import modules

from . import util
from . import model
from . import civitai
from . import ishortcut
from . import setting
from . import classification
from . import downloader
from . import civitai_action 

def on_ui(refresh_sc_list:gr.Textbox()):
    with gr.Column(scale=3):    
        with gr.Accordion("#", open=True) as model_title_name:               
            versions_list = gr.Dropdown(label="Model Version", choices=[setting.NORESULT], interactive=True, value=setting.NORESULT)             
            with gr.Row():
                update_information_btn = gr.Button(value="Update Model Information")       
                with gr.Accordion("Delete Civitai Shortcut", open=False):
                    shortcut_del_btn = gr.Button(value="Delete Shortcut")      
                                        
        with gr.Tabs():    
            with gr.TabItem("Images" , id="Model_Images"):                                 
                saved_gallery = gr.Gallery(show_label=False, elem_id="saved_gallery").style(grid=[setting.gallery_column],height=setting.information_gallery_height, object_fit=setting.gallery_thumbnail_image_style)    
                with gr.Row():
                    download_images = gr.Button(value="Download Images")
                    open_image_folder = gr.Button(value="Open Download Image Folder")                 
            with gr.TabItem("Description" , id="Model_Description"):                             
                description_html = gr.HTML()       
            with gr.TabItem("Download" , id="Model_Download"): 
                gr.Markdown("Downloadable Files")
                downloadable_files = gr.DataFrame(
                        headers=["","ID","Filename","Type","SizeKB","DownloadUrl"],
                        datatype=["str","str","str","str","str","str"], 
                        col_count=(6,"fixed"),
                        interactive=False,
                        type="array",
                    )                  
                filename_list = gr.CheckboxGroup (show_label=False , label="Model Version File", choices=[], value=[], interactive=True, visible=False)

                cs_foldername = gr.Dropdown(label='Download Folder Select', multiselect=None, choices=[setting.CREATE_MODEL_FOLDER] + classification.get_list(), value=setting.CREATE_MODEL_FOLDER, interactive=True)
                vs_folder = gr.Checkbox(label="Create individual version folder", value=False, visible=True , interactive=True)               
                vs_folder_name = gr.Textbox(label="Folder name to create", value="", show_label=False, interactive=True, lines=1, visible=False).style(container=True)
                download_model = gr.Button(value="Download", variant="primary")
                gr.Markdown("Downloading may take some time. Check console log for detail")     

                            
    with gr.Column(scale=1):            
        with gr.Tabs() as info_tabs:
            with gr.TabItem("Information" , id="Model_Information"):
                model_type = gr.Textbox(label="Model Type", value="", interactive=False, lines=1)
                trigger_words = gr.Textbox(label="Trigger Words", value="", interactive=False, lines=1).style(container=True, show_copy_button=True)
                civitai_model_url_txt = gr.Textbox(label="Model Url", value="", interactive=False , lines=1).style(container=True, show_copy_button=True)                   
                with gr.Row():            
                    with gr.Column():
                        with gr.Accordion("Classcification", open=True):
                            model_classification = gr.Dropdown(label='Classcification', show_label=False ,multiselect=True, interactive=True, choices=classification.get_list())
                            model_classification_update_btn = gr.Button(value="Update",variant="primary")

                        with gr.Accordion("Downloaded Version", open=True, visible=False) as downloaded_tab:                             
                            downloaded_info = gr.Textbox(interactive=False,show_label=False)
                            saved_openfolder = gr.Button(value="Open Download Folder",variant="primary", visible=False)
                with gr.Row():
                    with gr.Column():                                                    
                        refresh_btn = gr.Button(value="Refresh")                                                                                            

            with gr.TabItem("Image Information" , id="Image_Information"):      
                with gr.Column():            
                    img_file_info = gr.Textbox(label="Generate Info", interactive=True, lines=6).style(container=True, show_copy_button=True)
                    try:
                        send_to_buttons = modules.generation_parameters_copypaste.create_buttons(["txt2img", "img2img", "inpaint", "extras"])
                    except:
                        pass 
                
                            
    with gr.Row(visible=False): 
        selected_model_id = gr.Textbox()
        selected_version_id = gr.Textbox()
        
        # saved shortcut information  
        img_index = gr.Number(show_label=False)
        saved_images = gr.State() # 로드된것
        saved_images_url = gr.State() #로드 해야 하는것
        saved_images_meta = gr.State() # 생성 정보 로드
        
        # 트리거를 위한것
        hidden = gr.Image(type="pil")
        
        refresh_information = gr.Textbox()
        refresh_gallery = gr.Textbox()
    try:
        modules.generation_parameters_copypaste.bind_buttons(send_to_buttons, hidden,img_file_info)
    except:
        pass
   

    downloadable_files.select(
        fn=on_downloadable_files_select,
        inputs=[
            downloadable_files,
            filename_list
        ],
        outputs=[
            downloadable_files,
            filename_list,
        ]
    ) 

    cs_foldername.select(    
        fn=on_cs_foldername_select,
        inputs=None,
        outputs=[
            vs_folder,
            vs_folder_name
        ]          
    )
    
    download_model.click(
        fn=on_download_model_click,
        inputs=[
            selected_version_id,
            filename_list,            
            vs_folder,
            vs_folder_name,
            cs_foldername,
        ],
        outputs=[
            refresh_sc_list,
            refresh_information
        ]
    )  
        
    download_images.click(
        fn=on_download_images_click,
        inputs=[
            selected_model_id,
            saved_images_url              
        ],
        outputs=None 
    )
    
    gallery = refresh_gallery.change(
        fn=on_file_gallery_loading,
        inputs=[
            saved_images_url 
        ],
        outputs=[               
            saved_gallery,
            saved_images
        ]          
    )
        
    model_classification_update_btn.click(
        fn=on_model_classification_update_btn_click,
        inputs=[
            model_classification,
            selected_model_id
        ],
        outputs=[
            refresh_sc_list
        ]
    )
        
    # civitai saved model information start
    shortcut_del_btn.click(
        fn=on_shortcut_del_btn_click,
        inputs=[
            selected_model_id,
        ],
        outputs=[
            refresh_sc_list
        ]
    )
    
    update_information_btn.click(
        fn=on_update_information_btn_click,
        inputs=[
            selected_model_id,
        ],
        outputs=[
            selected_model_id,
            refresh_sc_list,
            # 이건 진행 상황을 표시하게 하기 위해 넣어둔것이다.
            saved_gallery,
            refresh_information #information update 용
        ]
    )
        
    selected_model_id.change(
        fn=on_load_saved_model,
        inputs=[
            selected_model_id,
        ],
        outputs=[
            selected_version_id,
            civitai_model_url_txt,
            downloaded_tab, 
            downloaded_info, 
            model_type, 
            versions_list,                    
            description_html,
            trigger_words,
            filename_list,
            downloadable_files,            
            model_title_name,                        
            refresh_gallery,
            saved_images_url,
            saved_images_meta,
            img_file_info,
            saved_openfolder,
            vs_folder,
            vs_folder_name,
            model_classification,
            cs_foldername
        ],
        cancels=gallery 
    )
    
    versions_list.select(
        fn=on_versions_list_select,
        inputs=[
            selected_model_id,
        ],
        outputs=[
            selected_version_id,
            civitai_model_url_txt,
            downloaded_tab, 
            downloaded_info, 
            model_type, 
            versions_list,                    
            description_html,
            trigger_words,
            filename_list,
            downloadable_files,            
            model_title_name,                        
            refresh_gallery,
            saved_images_url,
            saved_images_meta,
            img_file_info,
            saved_openfolder,
            vs_folder,
            vs_folder_name,
            model_classification,
            cs_foldername
        ],
        cancels=gallery
    )    

    #information update 용 start
    refresh_information.change(
        fn=on_load_saved_model,
        inputs=[
            selected_model_id,
        ],
        outputs=[
            selected_version_id,
            civitai_model_url_txt,
            downloaded_tab, 
            downloaded_info, 
            model_type, 
            versions_list,                    
            description_html,
            trigger_words,
            filename_list,
            downloadable_files,            
            model_title_name,                        
            refresh_gallery,
            saved_images_url,
            saved_images_meta,
            img_file_info,
            saved_openfolder,
            vs_folder,
            vs_folder_name,
            model_classification,
            cs_foldername
        ],
        cancels=gallery
    )
    
    refresh_btn.click(lambda :datetime.datetime.now(),None,refresh_information,cancels=gallery)    
    saved_gallery.select(on_gallery_select, saved_images, [img_index, hidden, info_tabs])
    hidden.change(on_civitai_hidden_change,[hidden,img_index,saved_images_meta],[img_file_info])
    saved_openfolder.click(on_open_folder_click,[selected_model_id,selected_version_id],None)  
    vs_folder.change(lambda x:gr.update(visible=x),vs_folder,vs_folder_name)
    
    open_image_folder.click(on_open_image_folder_click,[selected_model_id],None)
    
    return selected_model_id, refresh_information

def on_open_image_folder_click(modelid):
    if modelid:                
        model_info = ishortcut.get_model_info(modelid)
        if model_info:  
            model_name = model_info['name']
            image_folder = util.get_download_image_folder(model_name)
            if image_folder:
                util.open_folder(image_folder)
                
def on_downloadable_files_select(evt: gr.SelectData, df, filenames):
    # util.printD(evt.index)
    # index[0] # 행,열
    vid = None
    vname = None
    dn_name = None
    
    if df:
        vid = df[evt.index[0]][1]
        vname = df[evt.index[0]][2]
        dn_name = f"{vid}:{vname}"

    if vid:        
        if filenames:
            if dn_name in filenames:
                filenames.remove(dn_name)
                df[evt.index[0]][0] = '⬜️'
            else:
                filenames.append(dn_name)
                df[evt.index[0]][0] = '✅'
        else:
            filenames = [dn_name]    
            df[evt.index[0]][0] = '✅'

    return df, gr.update(value=filenames)

def on_download_images_click(model_id:str, images_url):
    msg = None
    if model_id:        
        model_info = ishortcut.get_model_info(model_id)              
        if not model_info:
            return

        if "name" not in model_info.keys():
            return
            
        downloader.download_image_file(model_info['name'], images_url)
    current_time = datetime.datetime.now() 

def on_download_model_click(version_id, file_name, vs_folder, vs_foldername, cs_foldername=None):
    msg = None
    if version_id:    
        # 프리뷰이미지와 파일 모두를 다운 받는다.
        if cs_foldername == setting.CREATE_MODEL_FOLDER:
            msg = civitai_action.download_file_thread(file_name, version_id, True, vs_folder, vs_foldername, None)
        else:
            msg = civitai_action.download_file_thread(file_name, version_id, False, False, None , cs_foldername)
            
        # 다운 받은 모델 정보를 갱신한다.    
        model.update_downloaded_model()

        current_time = datetime.datetime.now()    
        return gr.update(value=current_time),gr.update(value=current_time)    
    return gr.update(visible=True),gr.update(visible=True)

def on_cs_foldername_select(evt: gr.SelectData):
    if evt.value == setting.CREATE_MODEL_FOLDER:
        return gr.update(visible=True,value=False),gr.update(visible=False)
    return gr.update(visible=False,value=False),gr.update(visible=False)
    
def on_model_classification_update_btn_click(model_classification, modelid):
    
    if modelid:
        classification.clean_classification_shortcut(str(modelid))
        
    if model_classification and modelid:
        for name in model_classification:
            classification.add_classification_shortcut(name, str(modelid))
    current_time = datetime.datetime.now()
    return current_time
                
def on_open_folder_click(mid,vid):
    path = model.get_default_version_folder(vid)
    if path:
        util.open_folder(path)

def on_gallery_select(evt: gr.SelectData, civitai_images):
    return evt.index, civitai_images[evt.index], gr.update(selected="Image_Information")

def on_civitai_hidden_change(hidden, index, civitai_images_meta):
    info1,info2,info3 = modules.extras.run_pnginfo(hidden)
    if not info2:
        info2 = civitai_images_meta[int(index)]        
    return info2

def on_shortcut_del_btn_click(model_id):
    if model_id:
        delete_shortcut_model(model_id)            
    current_time = datetime.datetime.now()
    return current_time

def on_update_information_btn_click(modelid, progress=gr.Progress()):
    if modelid:
        update_shortcut_models([modelid],progress)  
                
        current_time = datetime.datetime.now()
        return gr.update(value=modelid),gr.update(value=current_time),gr.update(value=None),gr.update(value=current_time)
    return gr.update(value=modelid),gr.update(visible=True),gr.update(value=None),gr.update(visible=True)

def on_load_saved_model(modelid=None, ver_index=None):
    return load_saved_model(modelid, ver_index)

def on_versions_list_select(evt: gr.SelectData, modelid:str):
    return load_saved_model(modelid, evt.index)

def on_file_gallery_loading(image_url):
    chk_image_url = image_url
    if image_url:
        chk_image_url = [img if os.path.isfile(img) else setting.no_card_preview_image for img in image_url]   
        return chk_image_url, chk_image_url
    return None, None 
        
def load_saved_model(modelid=None, ver_index=None):
    if modelid:
        model_info,versionid,version_name,model_url,downloaded_versions,model_type,versions_list,dhtml,triger,files,title_name,images_url,images_meta,vs_foldername = get_model_information(modelid,None,ver_index)    
        if model_info:
            downloaded_info = None
            is_downloaded = False       
            is_visible_openfolder = False
                 
            if downloaded_versions:
                downloaded_info = "\n".join(downloaded_versions.values())
                
                if versionid in downloaded_versions:
                    is_visible_openfolder=True                
                        
            if downloaded_info:
                is_downloaded = True 
             
            current_time = datetime.datetime.now()
            
            classification_list = classification.get_classification_names_by_modelid(modelid)

            flist = list()
            downloadable = list()
            for file in files:            
                flist.append(f"{file['id']}:{file['name']}")
                downloadable.append(['✅',file['id'],file['name'],file['type'],round(file['sizeKB']),file['downloadUrl']])
                                
            return gr.update(value=versionid),gr.update(value=model_url),\
                gr.update(visible = is_downloaded),gr.update(value=downloaded_info),\
                gr.update(value=setting.get_ui_typename(model_type)),gr.update(choices=versions_list,value=version_name),gr.update(value=dhtml),\
                gr.update(value=triger),gr.update(choices=flist if flist else [], value=flist if flist else []), downloadable if len(downloadable) > 0 else None,\
                gr.update(label=title_name),\
                current_time,images_url,images_meta,gr.update(value=None),gr.update(visible=is_visible_openfolder),gr.update(value=False, visible=True),gr.update(value=vs_foldername, visible=False),\
                gr.update(choices=classification.get_list(),value=classification_list, interactive=True),\
                gr.update(choices=[setting.CREATE_MODEL_FOLDER] + classification.get_list(), value=setting.CREATE_MODEL_FOLDER)

    # 모델 정보가 없다면 클리어 한다.
    # clear model information
    return gr.update(value=None),gr.update(value=None),\
        gr.update(visible=False),gr.update(value=None),\
        gr.update(value=None),gr.update(choices=[setting.NORESULT], value=setting.NORESULT),gr.update(value=None),\
        gr.update(value=None),gr.update(value=None),None,\
        gr.update(label="#"),\
        None,None,None,gr.update(value=None),gr.update(visible=False),gr.update(value=False, visible=True),gr.update(value="",visible=False),\
        gr.update(choices=classification.get_list(),value=[], interactive=True),\
        gr.update(choices=[setting.CREATE_MODEL_FOLDER] + classification.get_list(), value=setting.CREATE_MODEL_FOLDER)

def get_model_information(modelid:str=None, versionid:str=None, ver_index:int=None):
    # 현재 모델의 정보를 가져온다.
    model_info = None
    version_info = None
    
    if modelid:
        model_info = ishortcut.get_model_info(modelid)        
        version_info = dict()
        if model_info:
            if not versionid and not ver_index:
                if "modelVersions" in model_info.keys():
                    version_info = model_info["modelVersions"][0]
                    if version_info["id"]:
                        versionid = version_info["id"]
            elif versionid:
                if "modelVersions" in model_info.keys():
                    for ver in model_info["modelVersions"]:                        
                        if versionid == ver["id"]:
                            version_info = ver                
            else:
                if "modelVersions" in model_info.keys():
                    if len(model_info["modelVersions"]) > 0:
                        version_info = model_info["modelVersions"][ver_index]
                        if version_info["id"]:
                            versionid = version_info["id"]
                            
    # 존재 하는지 판별하고 있다면 내용을 얻어낸다.
    if model_info and version_info:        
        version_name = version_info["name"]
        model_type = model_info['type']                    
        downloaded_versions = model.get_model_downloaded_versions(modelid)
        versions_list = list()            
        for ver in model_info['modelVersions']:
            versions_list.append(ver['name'])
        
        model_url = civitai.Url_Page() + str(modelid)        
        dhtml, triger, files = get_version_description(version_info,model_info)
        title_name = f"# {model_info['name']} : {version_info['name']}"
        images_url, images_meta = get_version_description_gallery(version_info)
        
        vs_foldername = setting.generate_version_foldername(model_info['name'],version_name,versionid)
                        
        return model_info, versionid,version_name,model_url,downloaded_versions,model_type,versions_list,dhtml,triger,files,title_name,images_url,images_meta, vs_foldername
    return None, None,None,None,None,None,None,None,None,None,None,None,None,None     
    
def get_version_description_gallery(version_info):
    modelid = None
    versionid = None
    ver_images = dict()
    
            
    if not version_info:
        return None, None

    if "modelId" in version_info.keys():
        modelid = str(version_info['modelId'])   
            
    if "id" in version_info.keys():
        versionid = str(version_info['id'])

    if "images" in version_info.keys():
        ver_images = version_info['images']

    images_url = list()
    images_meta = list()
    
    try:        
        for ver in ver_images:
            description_img = setting.get_image_url_to_shortcut_file(modelid,versionid,ver['url'])
            meta_string = ""
            if os.path.isfile(description_img):               
                meta_string = util.convert_civitai_meta_to_stable_meta(ver['meta'])
                images_url.append(description_img)
                images_meta.append(meta_string)                    
    except:
        return None, None
                
    return images_url, images_meta                  
    
def get_version_description(version_info:dict,model_info:dict=None):
    output_html = ""
    output_training = ""

    files = []
    
    html_typepart = ""
    html_creatorpart = ""
    html_trainingpart = ""
    html_modelpart = ""
    html_versionpart = ""
    html_descpart = ""
    html_dnurlpart = ""
    html_imgpart = ""
    html_modelurlpart = ""
    html_model_tags = ""
        
    model_id = None
    
    if version_info:        
        if 'modelId' in version_info:            
            model_id = version_info['modelId']  
            if not model_info:            
                model_info = ishortcut.get_model_info(model_id)

    if version_info and model_info:
        
        html_typepart = f"<br><b>Type: {model_info['type']}</b>"    
        model_url = civitai.Url_Page()+str(model_id)

        html_modelpart = f'<br><b>Model: <a href="{model_url}" target="_blank">{model_info["name"]}</a></b>'
        html_modelurlpart = f'<br><b><a href="{model_url}" target="_blank">Civitai Hompage << Here</a></b><br>'

        model_version_name = version_info['name']

        if 'trainedWords' in version_info:  
            output_training = ", ".join(version_info['trainedWords'])
            html_trainingpart = f'<br><b>Training Tags:</b> {output_training}'

        model_uploader = model_info['creator']['username']
        html_creatorpart = f"<br><b>Uploaded by:</b> {model_uploader}"

        if 'description' in version_info:  
            if version_info['description']:
                html_descpart = f"<br><b>Version : {version_info['name']} Description</b><br>{version_info['description']}<br>"

        if 'tags' in model_info:  
            model_tags = model_info["tags"]
            if len(model_tags) > 0:
                html_model_tags = "<br><b>Model Tags:</b>"
                for tag in model_tags:
                    html_model_tags = html_model_tags + f"<b> [{tag}]</b>"
                    
        # if 'tags' in model_info:  
        #     if model_info['tags']:
        #         model_tags = [tag["name"] for tag in model_info["tags"]]
        #         if len(model_tags) > 0:
        #             html_model_tags = "<br><b>Model Tags:</b>"
        #             for tag in model_tags:
        #                 html_model_tags = html_model_tags + f"<b> [{tag}] </b>"
                                        
        if 'description' in model_info:  
            if model_info['description']:
                html_descpart = html_descpart + f"<br><b>Description</b><br>{model_info['description']}<br>"
                    
        html_versionpart = f"<br><b>Version:</b> {model_version_name}"

        if 'files' in version_info:                                
            for file in version_info['files']:
                files.append(file)
                html_dnurlpart = html_dnurlpart + f"<br><a href={file['downloadUrl']}><b>Download << Here</b></a>"     
                            
        output_html = html_typepart + html_modelpart + html_versionpart + html_creatorpart + html_trainingpart + "<br>" +  html_model_tags + "<br>" +  html_modelurlpart + html_dnurlpart + "<br>" + html_descpart + "<br>" + html_imgpart
        
        return output_html, output_training, files            
    
    return "", None, None    
    
def upload_shortcut_by_files(files, register_information_only, progress):
    modelids = list()
    if files:
        shortcuts = []
        add_ISC = dict()
        ######
        for file in files:
            shortcuts = util.load_InternetShortcut(file.name)
            if shortcuts:
                for shortcut in shortcuts:
                    model_id = util.get_model_id_from_url(shortcut)
                    if model_id:                    
                        modelids.append(model_id)                    
        
        for model_id in progress.tqdm(modelids, desc=f"Civitai Shortcut"): 
            if model_id:                    
                add_ISC = ishortcut.add(add_ISC, model_id, register_information_only, progress)

        # util.printD(modelids)
        
        # for file in progress.tqdm(files, desc=f"Civitai Shortcut"):                        
        #     shortcut = util.load_InternetShortcut(file.name)            
        #     if shortcut:
        #         model_id = util.get_model_id_from_url(shortcut)                
        #         if model_id:                    
        #             add_ISC = ishortcut.add(add_ISC, model_id, register_information_only, progress)
        #             modelids.append(model_id)
                      
        ISC = ishortcut.load()
        if ISC:
            ISC.update(add_ISC)
        else:
            ISC = add_ISC            
        ishortcut.save(ISC)
        
    return modelids

def upload_shortcut_by_urls(urls, register_information_only, progress):
    modelids = list()
    if urls:
        add_ISC = dict()
        for url in progress.tqdm(urls, desc=f"Civitai Shortcut"):                        
            if url:                                  
                model_id = util.get_model_id_from_url(url)
                if model_id:                    
                    add_ISC = ishortcut.add(add_ISC, model_id, register_information_only, progress)
                    modelids.append(model_id)
                      
        ISC = ishortcut.load()
        if ISC:
            ISC.update(add_ISC)
        else:
            ISC = add_ISC            
        ishortcut.save(ISC)
        
    return modelids


def update_shortcut_model(modelid, progress = None):
    if modelid:
        add_ISC = ishortcut.add(None, str(modelid), False, progress)
        ISC = ishortcut.load()
        if ISC:
            ISC.update(add_ISC)
        else:
            ISC = add_ISC            
        ishortcut.save(ISC)
        
def update_shortcut_models(modelid_list, progress):
    if not modelid_list:       
        return
    
    # add_ISC = dict()                
    for k in progress.tqdm(modelid_list,desc="Updating Models Information"):        
        if k:                   
            add_ISC = ishortcut.add(None,str(k),False,progress)
            
            ISC = ishortcut.load()
            # hot fix and delete model
            # civitiai 에서 제거된 모델때문임
            # tags 를 변경해줘야함
            # 이슈가 해결되면 제거할코드
            if str(k) in ISC:
                ISC[str(k)]["tags"]=[]
                            
            if ISC:
                ISC.update(add_ISC)
            else:
                ISC = add_ISC            
            ishortcut.save(ISC)

def update_all_shortcut_model(progress):
    preISC = ishortcut.load()                           
    if not preISC:
        return
    
    modelid_list = [k for k in preISC]
    update_shortcut_models(modelid_list,progress)
                    
def delete_shortcut_model(modelid):
    if modelid:
        ISC = ishortcut.load()                           
        ISC = ishortcut.delete(ISC, modelid)
        ishortcut.save(ISC) 
            
def scan_downloadedmodel_to_shortcut(progress):        
    # util.printD(len(model.Downloaded_Models))
    if model.Downloaded_Models:
        modelid_list = [k for k in model.Downloaded_Models]
        update_shortcut_models(modelid_list,progress)
        
# def add_shortcut(modelid, progress):
#     if modelid:
#         add_ISC = ishortcut.add(None, str(modelid),False,progress)            
#         ISC = ishortcut.load()
#         if ISC:
#             ISC.update(add_ISC)
#         else:
#             ISC = add_ISC            
#         ishortcut.save(ISC) 
    
def is_new_version(modelid):
    if not modelid:    
        return False
    
    try:
        civitai_verinfo = civitai.get_latest_version_info_by_model_id(modelid)   
        saved_verinfo = ishortcut.get_latest_version_info_by_model_id(modelid)        
        # util.printD(civitai_verinfo['id'])
        # util.printD(saved_verinfo['id'])    
        if int(civitai_verinfo['id']) > int(saved_verinfo['id']):
            return True                    
    except:
        return False
    
    return False

    
            