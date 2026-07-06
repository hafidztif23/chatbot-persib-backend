import { useState, useRef, useEffect } from "react";
import DashboardLayout from "../components/layout/DashboardLayout";
import "../styles/knowledgebase.css";

// 12 Mock Documents for realistic pagination and display
const INITIAL_DOCUMENTS = [
  {
    id: 1,
    name: "Customer_Support_FAQ.pdf",
    type: "PDF",
    date: "Oct 24, 2023",
    size: "2.4 MB",
    status: "INDEXED",
    content: "Q: Bagaimana cara reset password?\nA: Anda dapat melakukan reset password melalui menu profil atau halaman login dengan mengklik 'Lupa Password'.\n\nQ: Berapa lama pengiriman tiket merch?\nA: Pengiriman merchandise berkisar antara 2-5 hari kerja tergantung pada wilayah pengiriman."
  },
  {
    id: 2,
    name: "Product_Catalog_2024.docx",
    type: "DOCX",
    date: "Oct 28, 2023",
    size: "4.8 MB",
    status: "PROCESSING",
    content: "KATALOG MERCHANDISE PERSIB 2024\n1. Jersey Home 2024 - Rp 450.000\n   Bahan premium breathable dry-fit, logo Persib woven HD, official merchandise tag.\n2. Jersey Away 2024 - Rp 450.000\n3. Syal Rajut Suporter - Rp 120.000\n4. Jaket Tracktop Maung - Rp 380.000"
  },
  {
    id: 3,
    name: "Internal_Guidelines.txt",
    type: "TXT",
    date: "Nov 02, 2023",
    size: "128 KB",
    status: "INDEXED",
    content: "STANDAR PELAYANAN CHATBOT MAUNGBOT\n1. Selalu gunakan bahasa yang sopan, ramah, dan bernuansa kekeluargaan (menggunakan panggilan 'Bobotoh').\n2. Jangan memberikan informasi spekulatif tentang transfer pemain yang belum diumumkan secara resmi.\n3. Pertanyaan tiket yang bermasalah harus segera diarahkan ke menu eskalasi."
  },
  {
    id: 4,
    name: "Persib_History_and_Trophies.pdf",
    type: "PDF",
    date: "Nov 08, 2023",
    size: "8.1 MB",
    status: "INDEXED",
    content: "SEJARAH PERSIB BANDUNG\nPersatuan Sepakbola Indonesia Bandung didirikan pada 14 Maret 1933. Persib merupakan salah satu klub pendiri PSSI. Gelar juara nasional diraih pada tahun 1937, 1961, 1986, 1990, 1994, 2014, dan juara terbaru Liga 1 Musim 2023/2024 di bawah asuhan Coach Bojan Hodak."
  },
  {
    id: 5,
    name: "Sponsor_Agreement_2024.pdf",
    type: "PDF",
    date: "Nov 15, 2023",
    size: "1.2 MB",
    status: "INDEXED",
    content: "DOKUMEN KONTRAK & SPONSORSHIP 2024\nKerja sama eksklusif dengan brand apparel lokal terkemuka dan sponsor utama perbankan. Ketentuan logo sponsorship pada jersey utama: Logo utama di bagian dada tengah berukuran 20x10cm, logo sekunder di lengan kiri 8x8cm."
  },
  {
    id: 6,
    name: "Squad_List_Second_Half_2024.xlsx",
    type: "XLSX",
    date: "Nov 20, 2023",
    size: "95 KB",
    status: "INDEXED",
    content: "DAFTAR SQUAD PERSIB LIGA 1 - PUTARAN KEDUA\n1. Kevin Ray Mendoza (GK) - 29 - Filipina\n2. Nick Kuipers (DF) - 2 - Belanda\n3. Gustavo Franca (DF) - 4 - Brasil\n4. Dedi Kusnandar (MF) - 11 - Indonesia\n5. Marc Klok (MF) - 23 - Indonesia (C)\n6. Ciro Alves (FW) - 77 - Brasil\n7. David da Silva (FW) - 19 - Brasil"
  },
  {
    id: 7,
    name: "Stadion_GBLA_Regulations.docx",
    type: "DOCX",
    date: "Nov 25, 2023",
    size: "2.1 MB",
    status: "INDEXED",
    content: "ATURAN KESELAMATAN & AKSES STADION GELORA BANDUNG LAUTAN API (GBLA)\n1. Penonton wajib menukar e-ticket menjadi gelang fisik di lokasi penukaran resmi sebelum kick-off.\n2. Dilarang membawa senjata tajam, kembang api, suar (flare), botol kaca, dan laser pointer.\n3. Pintu gerbang stadion dibuka 3 jam sebelum pertandingan dimulai."
  },
  {
    id: 8,
    name: "Ticketing_System_Troubleshoot.txt",
    type: "TXT",
    date: "Dec 02, 2023",
    size: "45 KB",
    status: "INDEXED",
    content: "PANDUAN SOLUSI PERMASALAHAN TIKET ONLINE\nGejala 1: Pembayaran berhasil tapi e-ticket tidak muncul di email.\nSolusi: Bobotoh disarankan cek folder Spam, atau login kembali ke aplikasi Persib App, lalu masuk ke menu 'Riwayat Transaksi'. Jika tetap kosong, arahkan ke eskalasi CS dengan melampirkan bukti transfer bank."
  },
  {
    id: 9,
    name: "Marketing_Campaign_L1.xlsx",
    type: "XLSX",
    date: "Dec 05, 2023",
    size: "140 KB",
    status: "INDEXED",
    content: "RENCANA KAMPANYE PROMOSI LIGA 1\n1. Promo Tiket Keluarga (Beli 3 gratis 1 untuk tribun samping selatan)\n2. Merchandise Bundling (Jersey Matchday + Syal diskon 15%)\n3. Konten Live Instagram Matchday (Kuis tebak skor berhadiah merchandise bertanda tangan pemain)"
  },
  {
    id: 10,
    name: "Persib_Store_Operational_FAQ.docx",
    type: "DOCX",
    date: "Dec 10, 2023",
    size: "3.2 MB",
    status: "INDEXED",
    content: "OPERASIONAL OUTLET PERSIB STORE\nAlamat: Jl. Sulanjana No. 17, Tamansari, Bandung.\nJam Buka: Senin - Minggu (10.00 - 21.00 WIB).\nKetentuan Retur: Penukaran barang cacat produksi maksimal 3 hari setelah pembelian dengan membawa struk fisik asli dan tag harga masih terpasang."
  },
  {
    id: 11,
    name: "Security_Briefing_Matchday.pdf",
    type: "PDF",
    date: "Dec 14, 2023",
    size: "5.5 MB",
    status: "INDEXED",
    content: "SOP PENGAMANAN PERTANDINGAN KATEGORI A (HIGH RISK)\nJumlah personel keamanan gabungan (TNI, Polri, Steward) minimal 1.500 personel. Ring 3 berada di luar gerbang luar stadion, Ring 2 di gerbang masuk tribun, dan Ring 1 di area sentel ban dan lapangan."
  },
  {
    id: 12,
    name: "Media_Accreditation_Policy.docx",
    type: "DOCX",
    date: "Dec 20, 2023",
    size: "1.7 MB",
    status: "INDEXED",
    content: "KEBIJAKAN AKREDITASI PERS & JURNALIS LIGA 1\nJurnalis peliput wajib memiliki kartu pers aktif dan terdaftar di sistem Liga Indonesia Baru (LIB). Pendaftaran ID Card pertandingan home Persib dilakukan secara online melalui Form Akreditasi H-3 sebelum kick-off."
  }
];

const ITEMS_PER_PAGE = 5;

function KnowledgeBase() {
  const [documents, setDocuments] = useState(INITIAL_DOCUMENTS);
  const [searchTerm, setSearchTerm] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedDoc, setSelectedDoc] = useState(null);
  const [isDragActive, setIsDragActive] = useState(false);
  const fileInputRef = useRef(null);

  // Set up mock status change for demonstration
  useEffect(() => {
    const processingItems = documents.filter(doc => doc.status === "PROCESSING");
    if (processingItems.length > 0) {
      const timers = processingItems.map(item => {
        return setTimeout(() => {
          setDocuments(prevDocs => 
            prevDocs.map(doc => 
              doc.id === item.id ? { ...doc, status: "INDEXED" } : doc
            )
          );
        }, 4000); // 4 seconds delay for realistic simulation
      });
      return () => timers.forEach(clearTimeout);
    }
  }, [documents]);

  // Handle Search Input Change
  const handleSearchChange = (e) => {
    setSearchTerm(e.target.value);
    setCurrentPage(1); // Reset to page 1 on new search
  };

  // Drag and Drop handlers
  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setIsDragActive(true);
    } else if (e.type === "dragleave") {
      setIsDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFiles(e.dataTransfer.files);
    }
  };

  // Click on dropzone triggers hidden file input
  const handleDropzoneClick = () => {
    fileInputRef.current.click();
  };

  const handleFileInputChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFiles(e.target.files);
    }
  };

  // Core file upload simulation
  const handleFiles = (fileList) => {
    const newDocs = Array.from(fileList).map((file, idx) => {
      const ext = file.name.substring(file.name.lastIndexOf('.')).toUpperCase();
      const name = file.name;
      const sizeStr = file.size > 1024 * 1024 
        ? `${(file.size / (1024 * 1024)).toFixed(1)} MB` 
        : `${(file.size / 1024).toFixed(0)} KB`;
      
      const today = new Date();
      const options = { month: 'short', day: '2-digit', year: 'numeric' };
      const formattedDate = today.toLocaleDateString('en-US', options);

      return {
        id: Date.now() + idx,
        name: name,
        type: ext.replace('.', ''),
        date: formattedDate,
        size: sizeStr,
        status: "PROCESSING",
        content: `Simulasi konten dokumen untuk file: ${name}.\nUkuran File: ${sizeStr}.\nDiunggah pada: ${formattedDate}.\nStatus saat ini sedang diekstrak dan di-embed ke dalam model Maung Bot.`
      };
    });

    setDocuments(prevDocs => [...newDocs, ...prevDocs]);
    setCurrentPage(1); // Go to page 1 to show the newly added file
    alert(`${newDocs.length} file berhasil ditambahkan ke daftar antrean upload (Simulasi).`);
  };

  // Delete Action
  const handleDelete = (id, name) => {
    if (window.confirm(`Apakah Anda yakin ingin menghapus dokumen "${name}"? Tindakan ini juga akan menghapus seluruh data embedding terkait.`)) {
      setDocuments(prevDocs => prevDocs.filter(doc => doc.id !== id));
      // Adjust page if deletion emptied the current page
      const remainingFiltered = filteredDocs.filter(doc => doc.id !== id);
      const totalPagesRemaining = Math.ceil(remainingFiltered.length / ITEMS_PER_PAGE);
      if (currentPage > totalPagesRemaining && totalPagesRemaining > 0) {
        setCurrentPage(totalPagesRemaining);
      }
    }
  };

  // View Action
  const handleView = (doc) => {
    setSelectedDoc(doc);
  };

  // Close Modal
  const closeModal = () => {
    setSelectedDoc(null);
  };

  // Filter items based on search query
  const filteredDocs = documents.filter(doc => 
    doc.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    doc.type.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Pagination Math
  const totalItems = filteredDocs.length;
  const totalPages = Math.ceil(totalItems / ITEMS_PER_PAGE);
  const startIndex = (currentPage - 1) * ITEMS_PER_PAGE;
  const endIndex = Math.min(startIndex + ITEMS_PER_PAGE, totalItems);
  const currentDocs = filteredDocs.slice(startIndex, startIndex + ITEMS_PER_PAGE);

  // File Icon selector based on extension
  const getFileIcon = (type) => {
    const typeUpper = type.toUpperCase();
    if (typeUpper === "PDF") {
      return (
        <div className="kb-doc-icon pdf" title="PDF File">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M14 2H6C4.89 2 4 2.9 4 4V20C4 21.1 4.89 22 6 22H18C19.1 22 20 21.1 20 20V8L14 2Z" fill="currentColor" opacity="0.15"/>
            <path d="M14 2H6C4.89 2 4 2.9 4 4V20C4 21.1 4.89 22 6 22H18C19.1 22 20 21.1 20 20V8M14 2L20 8M14 2V8H20" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            <text x="7" y="17" fill="currentColor" fontSize="5.5" fontWeight="bold" fontFamily="sans-serif">PDF</text>
          </svg>
        </div>
      );
    }
    if (typeUpper === "DOC" || typeUpper === "DOCX") {
      return (
        <div className="kb-doc-icon docx" title="Word File">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M14 2H6C4.89 2 4 2.9 4 4V20C4 21.1 4.89 22 6 22H18C19.1 22 20 21.1 20 20V8L14 2Z" fill="currentColor" opacity="0.15"/>
            <path d="M14 2H6C4.89 2 4 2.9 4 4V20C4 21.1 4.89 22 6 22H18C19.1 22 20 21.1 20 20V8M14 2L20 8M14 2V8H20" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            <text x="5.5" y="17" fill="currentColor" fontSize="4.5" fontWeight="bold" fontFamily="sans-serif">DOCX</text>
          </svg>
        </div>
      );
    }
    if (typeUpper === "XLS" || typeUpper === "XLSX") {
      return (
        <div className="kb-doc-icon xlsx" title="Excel File">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M14 2H6C4.89 2 4 2.9 4 4V20C4 21.1 4.89 22 6 22H18C19.1 22 20 21.1 20 20V8L14 2Z" fill="currentColor" opacity="0.15"/>
            <path d="M14 2H6C4.89 2 4 2.9 4 4V20C4 21.1 4.89 22 6 22H18C19.1 22 20 21.1 20 20V8M14 2L20 8M14 2V8H20" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            <text x="5.5" y="17" fill="currentColor" fontSize="5" fontWeight="bold" fontFamily="sans-serif">XLSX</text>
          </svg>
        </div>
      );
    }
    return (
      <div className="kb-doc-icon txt" title="Text File">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M14 2H6C4.89 2 4 2.9 4 4V20C4 21.1 4.89 22 6 22H18C19.1 22 20 21.1 20 20V8L14 2Z" fill="currentColor" opacity="0.15"/>
          <path d="M14 2H6C4.89 2 4 2.9 4 4V20C4 21.1 4.89 22 6 22H18C19.1 22 20 21.1 20 20V8M14 2L20 8M14 2V8H20" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          <text x="7" y="17" fill="currentColor" fontSize="5.5" fontWeight="bold" fontFamily="sans-serif">TXT</text>
        </svg>
      </div>
    );
  };

  return (
    <DashboardLayout>
      <div className="kb-container">
        
        {/* Header and Search Box */}
        <div className="kb-header">
          <h1 className="kb-title">Knowledge Base Management</h1>
          
          <div className="kb-search-wrapper">
            {/* Search Icon */}
            <svg className="kb-search-icon" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input 
              type="text" 
              placeholder="Search documents..." 
              className="kb-search-input"
              value={searchTerm}
              onChange={handleSearchChange}
            />
          </div>
        </div>

        {/* 2-Column Grid */}
        <div className="kb-grid">
          
          {/* LEFT: Upload Document Card */}
          <div className="kb-card kb-upload-card">
            <h2 className="kb-card-title">Upload Document</h2>
            
            {/* Dropzone with Drag and Drop Support */}
            <div 
              className={`kb-dropzone ${isDragActive ? "drag-active" : ""}`}
              onDragEnter={handleDrag}
              onDragLeave={handleDrag}
              onDragOver={handleDrag}
              onDrop={handleDrop}
              onClick={handleDropzoneClick}
            >
              <input 
                type="file" 
                ref={fileInputRef}
                style={{ display: "none" }}
                multiple
                accept=".txt,.pdf,.xlsx,.xls,.docx,.doc"
                onChange={handleFileInputChange}
              />
              
              <div className="kb-upload-icon-container">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                  <polyline points="17 8 12 3 7 8" />
                  <line x1="12" y1="3" x2="12" y2="15" />
                </svg>
              </div>
              
              <p className="kb-upload-text">Click to upload or drag and drop</p>
              <p className="kb-upload-subtext">PDF, DOCX, or TXT (Max. 10MB)</p>
              
              <button 
                type="button" 
                className="kb-upload-btn"
                onClick={(e) => {
                  e.stopPropagation(); // Avoid double click trigger
                  handleDropzoneClick();
                }}
              >
                Button 
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="5" y1="12" x2="19" y2="12" />
                  <polyline points="12 5 19 12 12 19" />
                </svg>
              </button>
            </div>

            {/* Status Info */}
            <div className="kb-status-section">
              <span className="kb-status-label">System Status</span>
              <div className="kb-status-value">
                <span className="kb-status-dot"></span>
                Training Engine Active
              </div>
            </div>
          </div>

          {/* RIGHT: Existing Documents Table Card */}
          <div className="kb-card kb-existing-card">
            <div className="kb-existing-header">
              <h2 className="kb-card-title" style={{ margin: 0 }}>Existing Documents</h2>
              <span className="kb-count-badge">{totalItems} DOCUMENTS</span>
            </div>

            {/* Documents Table */}
            <div className="kb-table-container">
              {currentDocs.length > 0 ? (
                <table className="kb-table">
                  <thead>
                    <tr>
                      <th style={{ width: "40%" }}>Document Name</th>
                      <th style={{ width: "10%" }}>Type</th>
                      <th style={{ width: "20%" }}>Upload Date</th>
                      <th style={{ width: "15%" }}>Status</th>
                      <th style={{ width: "15%" }}>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {currentDocs.map((doc) => (
                      <tr key={doc.id}>
                        <td>
                          <div className="kb-doc-name-cell" title={doc.name}>
                            {getFileIcon(doc.type)}
                            <span>{doc.name}</span>
                          </div>
                        </td>
                        <td>{doc.type}</td>
                        <td>{doc.date}</td>
                        <td>
                          <span className={`kb-badge ${doc.status.toLowerCase()}`}>
                            {doc.status}
                          </span>
                        </td>
                        <td>
                          <div className="kb-actions-cell">
                            <button 
                              className="kb-action-btn" 
                              title="Lihat Konten"
                              onClick={() => handleView(doc)}
                            >
                              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                                <circle cx="12" cy="12" r="3" />
                              </svg>
                            </button>
                            <button 
                              className="kb-action-btn delete" 
                              title="Hapus Dokumen"
                              onClick={() => handleDelete(doc.id, doc.name)}
                            >
                              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <polyline points="3 6 5 6 21 6" />
                                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                                <line x1="10" y1="11" x2="10" y2="17" />
                                <line x1="14" y1="11" x2="14" y2="17" />
                              </svg>
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              ) : (
                /* Empty state when search filters out everything */
                <div className="kb-empty-state">
                  <svg className="kb-empty-state-icon" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  <p className="kb-empty-state-title">Tidak ada dokumen ditemukan</p>
                  <p className="kb-empty-state-desc">Gunakan kata kunci pencarian yang lain atau unggah dokumen baru.</p>
                </div>
              )}
            </div>

            {/* Table Footer with Summary & Pagination */}
            {totalItems > 0 && (
              <div className="kb-existing-footer">
                <div className="kb-summary-text">
                  Showing {startIndex + 1} to {endIndex} of {totalItems} documents
                </div>
                
                <div className="kb-pagination">
                  <button 
                    className="kb-page-btn"
                    disabled={currentPage === 1}
                    onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                    title="Halaman Sebelumnya"
                  >
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                      <polyline points="15 18 9 12 15 6" />
                    </svg>
                  </button>
                  
                  {Array.from({ length: totalPages }).map((_, pageIdx) => {
                    const pageNum = pageIdx + 1;
                    return (
                      <button 
                        key={pageNum}
                        className={`kb-page-btn ${currentPage === pageNum ? "active" : ""}`}
                        onClick={() => setCurrentPage(pageNum)}
                      >
                        {pageNum}
                      </button>
                    );
                  })}

                  <button 
                    className="kb-page-btn"
                    disabled={currentPage === totalPages}
                    onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
                    title="Halaman Selanjutnya"
                  >
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                      <polyline points="9 18 15 12 9 6" />
                    </svg>
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* View Document Modal Details */}
        {selectedDoc && (
          <div className="kb-modal-overlay" onClick={closeModal}>
            <div className="kb-modal-content" onClick={(e) => e.stopPropagation()}>
              
              <div className="kb-modal-header">
                <h3 className="kb-modal-title">Pratinjau Dokumen</h3>
                <button className="kb-modal-close" onClick={closeModal} title="Tutup">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <line x1="18" y1="6" x2="6" y2="18" />
                    <line x1="6" y1="6" x2="18" y2="18" />
                  </svg>
                </button>
              </div>
              
              <div className="kb-modal-body">
                {/* Meta details */}
                <div className="kb-meta-grid">
                  <div className="kb-meta-item">
                    <span className="kb-meta-label">Nama File</span>
                    <span className="kb-meta-val">{selectedDoc.name}</span>
                  </div>
                  <div className="kb-meta-item">
                    <span className="kb-meta-label">Format Dokumen</span>
                    <span className="kb-meta-val">{selectedDoc.type}</span>
                  </div>
                  <div className="kb-meta-item">
                    <span className="kb-meta-label">Ukuran Berkas</span>
                    <span className="kb-meta-val">{selectedDoc.size}</span>
                  </div>
                  <div className="kb-meta-item">
                    <span className="kb-meta-label">Tanggal Unggah</span>
                    <span className="kb-meta-val">{selectedDoc.date}</span>
                  </div>
                </div>

                {/* Document Content Snippet */}
                <div className="kb-doc-content-section">
                  <span className="kb-doc-content-title">Ekstrak Konten Teks</span>
                  <pre className="kb-doc-content-box">{selectedDoc.content}</pre>
                </div>
              </div>
              
              <div className="kb-modal-footer">
                <button type="button" className="kb-btn-secondary" onClick={closeModal}>
                  Tutup
                </button>
              </div>

            </div>
          </div>
        )}

      </div>
    </DashboardLayout>
  );
}

export default KnowledgeBase;
