# Chatbot App

Aplikasi chatbot sederhana menggunakan React dan Vite.

## Fitur

- 🎨 Tampilan chatbot yang modern dan responsif
- 💬 Interface chat yang interaktif
- 🤖 Simulasi respons bot (static demo)
- ⚡ Fast refresh dengan Vite
- 📱 Responsive design untuk mobile dan desktop

## Teknologi yang Digunakan

- **React 19** - Library UI
- **Vite** - Build tool dan dev server
- **CSS3** - Styling dengan animasi dan gradient

## Cara Menjalankan

1. Install dependencies:
```bash
npm install
```

2. Jalankan development server:
```bash
npm run dev
```

3. Buka browser dan akses: `http://localhost:3000`

## Scripts

- `npm run dev` - Menjalankan development server
- `npm run build` - Build untuk production
- `npm run preview` - Preview production build

## Struktur Project

```
chatbot-app/
├── src/
│   ├── components/
│   │   ├── Chatbot.jsx
│   │   └── Chatbot.css
│   ├── App.jsx
│   ├── App.css
│   ├── main.jsx
│   └── index.css
├── index.html
├── vite.config.js
└── package.json
```

## Next Steps

- [ ] Integrasi dengan backend API
- [ ] Tambah fitur upload file
- [ ] Implementasi real-time chat dengan WebSocket
- [ ] Tambah autentikasi user
- [ ] Simpan riwayat chat

## Catatan

Saat ini aplikasi menggunakan respons bot statis untuk demo. Nantinya akan diintegrasikan dengan backend untuk respons yang dinamis.
