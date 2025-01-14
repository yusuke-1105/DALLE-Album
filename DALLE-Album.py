from openai import OpenAI, AzureOpenAI
import streamlit as st
from PIL import Image
import requests
import asyncio
import atexit
import os

# セッション状態の初期化
if 'page' not in st.session_state:
    st.session_state.page = 'main'
if 'selected_tags' not in st.session_state:
    st.session_state.selected_tags = set()
if 'api_type' not in st.session_state:
    st.session_state.api_type = 'なし'
if 'api_key' not in st.session_state:
    st.session_state.api_key = ''
if 'resource_name' not in st.session_state:
    st.session_state.resource_name = ''
if 'base_prompt' not in st.session_state:
    st.session_state.base_prompt = "Create an album cover with the following style: "
# セッション状態の初期化部分に追加
if 'ordered_tags' not in st.session_state:
    st.session_state.ordered_tags = []
if 'prompt_area' not in st.session_state:
    st.session_state.number = 1

# 環境変数にAPIキーを設定
os.environ['OPENAI_API_KEY'] = st.session_state.api_key
os.environ['AZURE_OPENAI_API_KEY'] = st.session_state.api_key
os.environ['AZURE_OPENAI_ENDPOINT'] = st.session_state.resource_name

# 終了時に環境変数をクリア
def clear_env_vars():
    os.environ['OPENAI_API_KEY'] = ''
    os.environ['AZURE_OPENAI_API_KEY'] = ''
    os.environ['AZURE_OPENAI_ENDPOINT'] = ''

atexit.register(clear_env_vars)

# メインのディレクトリ
ROOT_DIR = "."
# ROOT_DIR = "."

# フォルダの作成
if not os.path.exists(ROOT_DIR + "/Pic-1"):
    os.makedirs(ROOT_DIR + "/Pic-1")
if not os.path.exists(ROOT_DIR + "/Pic-2"):
    os.makedirs(ROOT_DIR + "/Pic-2")
if not os.path.exists(ROOT_DIR + "/history"):
    os.makedirs(ROOT_DIR + "/history")

# 利用可能なタグ一覧
JTAGS = [
    "ポップ", "ロック", "ジャズ", "クラシック", "モダン",
    "ヒップホップ","R&B", "EDM", "JPOP", "KPOP",
    "嬉しい", "悲しい", "怒り", "恐怖", "驚き",
    "1970's", "1980's", "1990's", "2000's", "2010's",
    "猫", "犬", "鳥", "牛", "豚",
    "CG", "アニメ", "写真", "水彩", "油絵",
    "赤", "青", "黄", "緑", "紫",
    "愛", "夢", "未来", "過去", "自然",
    "宇宙", "海", "山", "都市", "田舎"
]

ETAGS_DICT = {
    "ポップ": "pop", "ロック": "rock", "ジャズ": "jazz", "クラシック": "classical", "モダン": "modern",
    "ヒップホップ": "hip-hop", "R&B": "r&b", "EDM": "edm", "JPOP": "j-pop", "KPOP": "k-pop",
    "嬉しい": "happy", "悲しい": "sad", "怒り": "angry", "恐怖": "fear", "驚き": "surprise",
    "1970's": "1970s", "1980's": "1980s", "1990's": "1990s", "2000's": "2000s", "2010's": "2010s",
    "猫": "cat", "犬": "dog", "鳥": "bird", "牛": "cow", "豚": "pig",
    "CG": "Computer Graphics", "アニメ": "anime", "写真": "realistic image", "水彩": "watercolor", "油絵": "oil-painting",
    "赤": "red", "青": "blue", "黄": "yellow", "緑": "green", "紫": "purple",
    "愛": "love", "夢": "dream", "未来": "future", "過去": "past", "自然": "nature",
    "宇宙": "space", "海": "sea", "山": "mountain", "都市": "city", "田舎": "country"
}

# update_prompt() 関数を修正
def update_prompt():
    base = st.session_state.base_prompt
    if ":" in base:
        base = base.split(":")[0] + ":"
    
    if st.session_state.ordered_tags:
        return f"{base} {', '.join(st.session_state.ordered_tags)}"
    return base

async def generate_image(prompt):
    if st.session_state.api_type == 'なし':
        return 'image.jpg'
    
    try:

        if st.session_state.api_type == 'OpenAI':
            client = OpenAI(
                api_key=os.getenv("OPENAI_API_KEY")
            )
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )

            return response.data[0].url
        elif st.session_state.api_type == 'Azure OpenAI Service':
            # Azure OpenAI Service client setup
            client = AzureOpenAI(
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
                api_version="2024-02-01",
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
            )
            response = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )

            return response.data[0].url
    except Exception as e:
        st.error(f"Error generating image: {str(e)}")
        return None

# 古い画像の下部に新しい画像を繋ぎ合わせる
def append_images(image):
    try:
        roll_image = Image.open(f'{ROOT_DIR}/history/image.jpg')
        width, height = roll_image.size
        result = Image.new('RGB', (width, height + image.size[1]))
        result.paste(roll_image, (0, 0))
        result.paste(image, (0, height))
        result.save(f'{ROOT_DIR}/history/image.jpg')
        return
    except:
        image.save(f'{ROOT_DIR}/history/image.jpg')
        return

def main():
    if st.session_state.page == 'settings':
        st.title('API設定')
        
        st.session_state.api_type = st.radio(
            "API種別を選択してください",
            ('なし', 'OpenAI', 'Azure OpenAI Service')
        )

        st.session_state.resource_name = st.text_input(
            "Azure OpenAI Serviceのエンドポイント",
            disabled=(st.session_state.api_type != 'Azure OpenAI Service'),
            value=st.session_state.resource_name
        )

        st.session_state.api_key = st.text_input(
            "APIキー",
            type="password",
            disabled=(st.session_state.api_type == 'なし'),
            value=st.session_state.api_key
        )
        
        st.button('送信 or 戻る', on_click=lambda: setattr(st.session_state, 'page', 'main'))
            
    else:  # main page
        st.title('アルバムジャケット生成 beta')
        
        _, col2 = st.columns([6, 1])
        with col2:
            st.button('API設定', on_click=lambda: setattr(st.session_state, 'page', 'settings'))
        
        # プロンプト入力エリア ----------------
        current_prompt = st.text_area("基本プロンプト", value=update_prompt(), key="prompt_area")
        # 基本プロンプト部分のみを保存
        if ":" in current_prompt:
            st.session_state.base_prompt = current_prompt.split(":")[0] + ":"
        else:
            st.session_state.base_prompt = current_prompt

        # フォルダ番号選択エリア ----------------
        st.session_state.number = st.selectbox('フォルダ番号', [1, 2], index=st.session_state.number - 1, key='pic_number')
        
        # タグ選択エリア -----------------------
        st.write("スタイルタグを選択してください：")
        st.write("ジャンル×2、感情、時代、動物、画風、色、その他×2")
        cols = st.columns(5)
        for i, tag in enumerate(JTAGS):
            with cols[i % 5]:
                if st.button(
                    tag,
                    type="primary" if tag in st.session_state.selected_tags else "secondary",
                    key=f"tag_{tag}"
                ):
                    t = ETAGS_DICT[tag] if tag in ETAGS_DICT else tag
                    if t in st.session_state.selected_tags:
                        st.session_state.selected_tags.remove(t)
                        st.session_state.ordered_tags.remove(t)
                    else:
                        st.session_state.selected_tags.add(t)
                        st.session_state.ordered_tags.append(t)
                    st.rerun()
        
        # 画像生成ボタン -----------------------
        if st.button('生成', icon='🎨'):
            with st.spinner('画像を生成中...'):
                image_url = asyncio.run(generate_image(current_prompt))
                if image_url:
                    if image_url == 'image.jpg':
                        image = Image.open('images/image.jpg')
                        st.image(image, caption='アルバムジャケット')
                        image.save(f'{ROOT_DIR}/Pic-{st.session_state.number}/image.jpg')
                        st.session_state.number = st.session_state.number % 2 + 1
                        append_images(image)
                    else:
                        image = Image.open(requests.get(image_url, stream=True).raw)
                        st.image(image, caption='アルバムジャケット')
                        image.save(f'{ROOT_DIR}/Pic-{st.session_state.number}/image.jpg')
                        st.session_state.number = st.session_state.number % 2 + 1
                        append_images(image)

if __name__ == "__main__":
    main()