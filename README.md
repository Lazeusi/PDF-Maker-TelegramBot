<p align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&height=180&section=header&text=PDF%20Generator%20Bot&fontSize=45&fontAlignY=35&animation=twinkling&fontColor=fff" />
</p>

<h3 align="center">🚀 Advanced Telegram Bot for PDF Generator</h3>

<p align="center">
  <b>Built with:</b> Aiogram v3.22.0 • Async • MongoDB  
</p>


# 📖 Overview  

A **powerful Telegram bot** built with **Aiogram 3.22+** and **MongoDB**, designed to convert texts and images into high-quality PDF files with full Persian (RTL) support and an advanced admin system.



## 🚀 Features  

### 🧠 PDF Maker  
- Convert **texts and images** into a single PDF  
- Full **Persian (RTL)** support via `arabic-reshaper` and `python-bidi`  
- Choose **font**, **font size**, and **page order**  
- **Preview and delete** pages before building the PDF  
- Automatically sends the generated PDF to the user  



### ⚙️ Admin Panel  
Accessible only by the **Owner**.

#### 🔧 Commands:
| Command | Description |
|----------|-------------|
| `/active_owner` | Activate yourself as the **Owner** (only once). |
| `/admin` | Open the Admin Panel (Owner only). |



### 🧩 Admin Panel Features  
- 👤 Add or remove **admins**  
- 📢 Manage **forced-join channels** (public or private)  
- 💬 Private channels can be added by **forwarding a message** from them  
- 🔗 Public channels can be added using **@username**  
- 🗑️ Remove or edit channels dynamically via inline buttons  



## 💾 Database  
Powered by **MongoDB (Motor async driver)**  

**Collections:**
- `users` → user data  
- `admins` → admin list  
- `channels` → forced-join channels  



## ⚙️ Installation  

```bash
git clone https://github.com/Lazeusi/PDF-Maker-TelegramBot.git
cd PDF-Maker-TelegramBot
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```


Create a .env file with:
```
BOT_TOKEN=your_bot_token_here
MONGO_URL=mongodb+srv://username:password@cluster.mongodb.net
DB_NAME=PDF_MAKER_DB
```

## 🏁 Run the Bot
```
python main.py
👑 Owner Activation
```
Send the command: `/active_owner`
Then access the admin panel with: `/admin`

Inside the panel, you can: **Add or remove admins**, **Manage forced-join channels**, **Check user membership**

## 🛠️ Tech Stack
| Component | Description |
|------------|-------------|
| 🐍 Python 3.13.9 | Core language |
| 🤖 Aiogram 3.22.0 | Telegram Bot framework |
| 🍃 MongoDB + Motor| Database |
| ⚡ Async / Await | Full async architecture |
| 🧰 Logging & Error Handling | Custom structured logging system |
| 🎈 ReportLab | PDF generation |
| 💬 Arabic-reshaper / Python-bidi | RTL text rendering |

## 💡 Future Plans

**✨ Custom PDF templates**

**🧾 Add watermarks and branding**

**☁️ Cloud storage for generated PDFs**

**🌐 Web dashboard (FastAPI-based)**


## 🧑‍💻 Author

Shayan
> Python Developer — Focused on Aiogram, FastAPI, and automation projects.
 | 🔗 GitHub: github.com/Lazeusi
 | 🐍 Telegram: @lazeusi

## ❤️ Support
If you like this project, consider giving it a ⭐ on GitHub!
Contributions, ideas, and PRs are always welcome 🙌


<p align="center"> <img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&height=120&section=footer"/> </p>