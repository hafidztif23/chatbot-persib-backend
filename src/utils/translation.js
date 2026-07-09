const TRANSLATIONS = {
  // Indonesian (default, referensi_bahasa = 1)
  1: {
    // Sidebar
    new_chat: "Obrolan Baru",
    menu_utama: "MENU UTAMA",
    chat_sekarang: "Chat Sekarang",
    knowledge_base: "Knowledge Base",
    user_menu: "USER",
    edit_profil: "Edit Profil",
    pengaturan_menu: "PENGATURAN",
    settings: "Settings",
    logout: "Keluar",

    // Settings Page
    settings_title: "Pengaturan",
    update_btn: "Perbarui →",
    save_success: "Pengaturan berhasil disimpan!",
    card_language: "Bahasa",
    system_lang: "Bahasa Sistem",
    card_tone: "Nada Bicara",
    tone_style: "Gaya Bahasa",
    formality_level: "Tingkat Formalitas",
    card_notifications: "Notifikasi",
    enable_notifications: "Aktifkan Notifikasi",

    // Chatbot Page
    chatbot_welcome: "Mulai obrolan baru dengan Maung Chat",
    chatbot_subtitle: "Tanya seputar taktik, jadwal pertandingan, info pemain, atau ngobrol seru bareng AI Legenda Persib.",
    chatbot_placeholder: "Ajukan Pertanyaan atau Mulai Obrolan...",
    suggested_q1: "Siapa top skorer Persib musim ini?",
    suggested_q2: "Bagaimana regulasi Stadion GBLA",
    suggested_q3: "Kapan jadwal Persib vs Persija?",
    suggested_q4: "Stok Merchandise Persib Bandung",
  },
  // English (referensi_bahasa = 2)
  2: {
    // Sidebar
    new_chat: "New Chat",
    menu_utama: "MAIN MENU",
    chat_sekarang: "Chat Now",
    knowledge_base: "Knowledge Base",
    user_menu: "USER",
    edit_profil: "Edit Profile",
    pengaturan_menu: "SETTINGS",
    settings: "Settings",
    logout: "Logout",

    // Settings Page
    settings_title: "Settings",
    update_btn: "Update →",
    save_success: "Settings saved successfully!",
    card_language: "Language",
    system_lang: "System Language",
    card_tone: "Tone",
    tone_style: "Tone Style",
    formality_level: "Formality Level",
    card_notifications: "Notifications",
    enable_notifications: "Enable Notifications",

    // Chatbot Page
    chatbot_welcome: "Start a new chat with Maung Chat",
    chatbot_subtitle: "Ask about tactics, match schedules, player info, or have a fun chat with Persib AI Legends.",
    chatbot_placeholder: "Ask a Question or Start Chatting...",
    suggested_q1: "Who is Persib's top scorer this season?",
    suggested_q2: "Regulation of GBLA Stadium",
    suggested_q3: "When is Persib vs Persija match?",
    suggested_q4: "How Many Stock Merchandise Persib Bandung",
  }
};

export const getTranslation = (langCode) => {
  const code = langCode === 2 ? 2 : 1;
  return TRANSLATIONS[code];
};
