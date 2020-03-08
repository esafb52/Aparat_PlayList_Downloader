from bs4 import BeautifulSoup
from time import sleep
import requests as req
import argparse
import os
import re
import wget

BASE_URL = "https://www.aparat.com"
HEADERS = {'user-agent': 'Mozilla/6.0 (Windows NT 10.0; Win64; x64; rv:58.0) Gecko/20100101 Chrome/66'}
OUT_DIR_PATH = ""
LOG_FILE_FOR_LINKS = "download_links.txt"
LOG_FILE_FOR_NAME = "download_file_names.txt"
# for separate saving name and link in txt file
LINE_SEP = "<@@@>"


def get_all_playlist_episode_links_and_titles(url):
    """
    get all a tag by request playlist url
    :param url: play list link such as https://www.aparat.com/v/VgFSr?playlist=110553
    :return: request result form url
    """
    res = req.get(url, headers=HEADERS)
    links = BeautifulSoup(res.content, 'html.parser').find_all('div', attrs={'class': 'playlist-body'})[0]
    playlist_links = links.find_all('a', attrs={'class': 'title'})
    lst_res = []
    for item in playlist_links:
        item_link = BASE_URL + (item.get('href'))
        item_name = (item.get('title'))
        lst_res.append({"filename": item_name, "link": item_link})
    return lst_res


def get_all_episode_download_links(lts_episode_links):
    """
    generate base link for each episode in playlist  as list links form lst_web_content
    :param lts_episode_links:request result
    :return: list of item contain dict name and txt links of episodes
    """
    lst_download_links = []
    lst_file_names = []
    counter = 0
    for episode_link in lts_episode_links:
        try:
            link = episode_link['link']
            web_file_title = episode_link['filename']
            download_link_info = generate_episode_mp4_file_link_and_name(link)
            file_name = download_link_info['filename']
            lst_download_links.append(download_link_info)
            lst_file_names.append(file_name + LINE_SEP + web_file_title)
            counter += 1
            print("{0} :> add to download list :> {1}".format(counter, link))
        except Exception as e:
            print(e)
    lst_pure_links = [link['link'] for link in lst_download_links]
    log_content_to_txt_file(lst_pure_links, LOG_FILE_FOR_LINKS)
    log_content_to_txt_file(lst_file_names, LOG_FILE_FOR_NAME)
    lst_download_links_final = list(filter(lambda item: item['link'] is not None, lst_download_links))
    return lst_download_links_final


def generate_episode_mp4_file_link_and_name(url):
    """
    generate episode mp4 file link form apart site by quality
    start form 720p and end with 1080p (1080p is end because for large size)
    :param url: episode url link
    :return: list contain dict for files with name and url of file
    """
    quality_range = ('720p', '480p', '360p', '240p', '1080p')
    request_res = req.get(url, headers=HEADERS)
    soup_result = BeautifulSoup(request_res.content, "html.parser")
    final_links_result = soup_result.find_all('div', attrs={'class': "dropdown-content"})[0].find_all('a')
    for file_quality in quality_range:
        for my_link in final_links_result:
            file_link = str(my_link.get('href'))
            file_name = generate_simple_file_name(file_link)
            if file_quality in file_link:
                return {"filename": file_name, "link": file_link}
    return {"filename": None, "link": None}


def download_play_list_files(lst_download_links_dict, out_path_dir):
    """
    download file form list contain dict
    :param lst_download_links_dict:
    :param out_path_dir: save download files
    :return: no this !!!
    """
    if not os.path.exists(out_path_dir):
        os.mkdir(out_path_dir)
    counter = 0
    for download_link in lst_download_links_dict:
        try:
            url_link = download_link["link"]
            file_name = generate_simple_file_name(url_link) + '.mp4'
            file_final_path = os.path.join(out_path_dir, file_name)
            if not os.path.exists(file_final_path):
                counter += 1
                print("{0} :> download start : {1} ".format(counter, url_link))
                wget.download(url_link, file_final_path)
                sleep(2)
            else:
                print(download_link["filename"] + ' file already exists')
        except Exception as e:
            print(e, download_link["filename"])


def clean_persian_name_from_extra_char(farsi_name):
    """
    remove extra char for farsi name
    :param farsi_name:
    :return: clean str of farsi file name
    """
    if farsi_name is not None:
        clean_extra_char_farsi_name = re.sub(r"[^\w.  ]+", '', farsi_name)
        final_farsi_name = str(clean_extra_char_farsi_name).strip() + '.mp4'
        return final_farsi_name
    else:
        print('invalid name !!!')


def generate_simple_file_name(episode_link):
    """
    generate final download file name
    :param episode_link:
    :return: simple_name and file_name
    """
    file_name = str(os.path.basename(episode_link))
    simple_name = file_name.split('-')[0]
    return simple_name


def rename_download_files_to_persian_name(txt_file, dir_path):
    """
    rename download file to file title in page for better using
    :param txt_file: txt file contain file names use LOG_FILE_FOR_NAME
    :param dir_path: dir path that contain download playlist file
    :return: not things
    """
    if os.path.exists(txt_file):
        file = open(txt_file, 'r', encoding='utf-8')
        lst_file_names = file.readlines()
        for item in lst_file_names:
            english_name, farsi_name = item.split(LINE_SEP)
            final_farsi_name = clean_persian_name_from_extra_char(farsi_name)
            current_file_name = os.path.join(dir_path, english_name + '.mp4')
            if os.path.exists(current_file_name):
                os.rename(current_file_name, os.path.join(dir_path, final_farsi_name))
            else:
                print(english_name + "  not find  !!!!!!!!!! ")


def log_content_to_txt_file(lst_links_text, my_file):
    """
    log all content to txt file
    :param lst_links_text: list of item to save in txt file
    :param my_file:file name
    :return: none
    """
    try:
        ls = list(lst_links_text)
        with open(my_file, 'w', encoding="utf-8")as f:
            for item in ls:
                if item is not None:
                    f.write(item + "\n")
    except Exception as e:
        print("error {0}".format(e))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog="Aparat PlayList Downloader")
    parser.add_argument("-url", type=str, help="playlist url you want to download !!! ")
    parser.add_argument("-out", type=str, help=" output folder to save download files ")
    args = parser.parse_args()
    if args.url is None:
        print('usage example:')
        print("aparat.exe -url=https://www.aparat.com/v/VgFSr?playlist=110553")
        print('or')
        print("python App.py -url=https://www.aparat.com/v/VgFSr?playlist=110553 -out=d:\\117849")
    else:
        if args.out is None:
            args.out = os.getcwd()
        playlist_code = str(args.url).split('=')[1]
        out_dir_path = os.path.join(args.out, "{0}_Aparat_Files".format(playlist_code))
        PLAYLIST_URL = args.url
        print("start generate download links")
        web_req_result = get_all_playlist_episode_links_and_titles(PLAYLIST_URL)
        lst_links = get_all_episode_download_links(web_req_result)
        print("start download files !!! \n")
        download_play_list_files(lst_links, out_dir_path)
        rename_download_files_to_persian_name(LOG_FILE_FOR_NAME, out_dir_path)
        print("end downloads !!!")
