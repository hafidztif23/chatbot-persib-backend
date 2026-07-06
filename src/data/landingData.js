import ticketingImg from "../image/ticketing.jpg";
import membershipImg from "../image/membership.jpg";
import scheduleImg from "../image/schedule.jpg";
import merchImg from "../image/merch.png";
import stadiumImg from "../image/stadium.jpg";
import instagramIcon from "../image/instagram3.png";
import linkedinIcon from "../image/linkedin3.png";
import youtubeIcon from "../image/youtube2.png";
import twitterIcon from "../image/X2.png";
import facebookIcon from "../image/facebook2.png";

export const landingData = {
  navLinks: [
    { label: "Home", href: "#home" },
    { label: "Features", href: "#features" },
    { label: "Review", href: "#review" },
    { label: "FAQ", href: "#faq" },
    { label: "Contact", href: "#contact" },
  ],
  testimonials: [
    {
      name: "Rian Hidayat",
      username: "@rian_bobotoh",
      text: "Gak perlu lagi nunggu admin medsos bales DM buat tau jadwal tanding. Tanya Maung Bot, detik itu juga dapet jawabannya. Mantap!"
    },
    {
      name: "Siti Aminah",
      username: "@sitia_persib",
      text: "Pertama kali beli tiket online agak bingung, tapi dibimbing langkah demi langkah sama bot-nya. Sangat membantu buat fans awam kaya saya."
    },
    {
      name: "Budi Santoso",
      username: "@budi_viking",
      text: "Akurasi infonya juara. Soal regulasi stadion yang sering berubah pun Maung Bot selalu update. Wajib pakai sih kalau mau nonton ke GBLA."
    },
    {
      name: "Kang Mus",
      username: "@muslihat_bdg",
      text: "Asli ini ngebantu banget buat cek klasemen sama statistik pemain tanpa harus buka-buka web lain. Edun pisan Maung Bot!"
    }
  ],
  useCases: [
    { image: ticketingImg, title: "Ticketing", desc: "How to buy" },
    { image: membershipImg, title: "Membership", desc: "Benefits" },
    { image: scheduleImg, title: "Match Schedule", desc: "Who is next" },
    { image: merchImg, title: "Merchandise", desc: "Limited editions" },
    { image: stadiumImg, title: "Stadium Rules", desc: "Forbidden items" },
  ],
  faqs: [
    { 
      question: "Apakah Maung Bot tersedia 24 jam?", 
      answer: "Tentu, Maung Bot tersedia 24 jam sehari, 7 hari seminggu untuk menjawab seluruh pertanyaan Bobotoh secara instan." 
    },
    { 
      question: "Informasi apa saja yang bisa ditanyakan?", 
      answer: "Persib Bandung akan segera mengumumkan seluruh informasi. Mulai dari jadwal, tiket, merchandise, hingga aturan stadion. Informasi yang diberikan merupakan respons dari knowledge base resmi Maung Bot." 
    },
    { 
      question: "Seberapa akurat jawaban Maung Bot?", 
      answer: "Sangat akurat karena didukung oleh teknologi Retrieval-Augmented Generation (RAG) yang menarik data langsung dari dokumen resmi klub." 
    },
    { 
      question: "Apakah saya perlu akun untuk menggunakan Maung Bot?", 
      answer: "Beberapa fitur umum bisa diakses tanpa akun, namun untuk bantuan tiket dan keanggotaan spesifik, disarankan untuk login." 
    },
  ],
  footerSocials: [
    { href: "https://www.facebook.com/PERSIB", icon: facebookIcon, label: "Facebook" },
    { href: "https://www.instagram.com/persib/?hl=id", icon: instagramIcon, label: "Instagram" },
    { href: "https://x.com/persib", icon: twitterIcon, label: "X / Twitter" },
    { href: "https://id.linkedin.com/company/persib", icon: linkedinIcon, label: "LinkedIn" },
    { href: "https://www.youtube.com/channel/UCq9VjkTSRBvlyr0sSXwm8Kw", icon: youtubeIcon, label: "YouTube" },
  ],
  footerLinks: [
    {
      title: "Produk",
      items: [
        { label: "Fitur Utama", href: "#" },
        { label: "AI Legends", href: "#" },
        { label: "Tiket VIP", href: "#" },
        { label: "Merchandise", href: "#" },
      ]
    },
    {
      title: "Perusahaan",
      items: [
        { label: "Tentang Kami", href: "#" },
        { label: "Karier", href: "#" },
        { label: "Kontak", href: "#" },
        { label: "Press Kit", href: "#" },
      ]
    },
    {
      title: "Legal",
      items: [
        { label: "Privasi", href: "#" },
        { label: "Ketentuan", href: "#" },
        { label: "Keamanan", href: "#" },
      ]
    }
  ]
};