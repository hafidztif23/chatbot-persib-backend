import { useState, useRef, useEffect } from "react";
import DashboardLayout from "../components/layout/DashboardLayout";
import "../styles/knowledgebase.css";
import { docsAPI } from "../services/api";

const ITEMS_PER_PAGE = 5;

function KnowledgeBase() {
  const [documents, setDocuments] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedDoc, setSelectedDoc] = useState(null);
  const [isDragActive, setIsDragActive] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const fileInputRef = useRef(null);
  const [customModal, setCustomModal] = useState({
    isOpen: false,
    title: "",
    message: "",
    type: "info", // "confirm" | "success" | "error" | "info"
    onConfirm: null,
    onCancel: null
  });

  const showCustomAlert = (title, message, type = "info") => {
    setCustomModal({
      isOpen: true,
      title: title,
      message: message,
      type: type,
      onConfirm: () => {
        setCustomModal(prev => ({ ...prev, isOpen: false }));
      },
      onCancel: null
    });
  };

  const fetchDocuments = async () => {
    setIsLoading(true);
    try {
      const data = await docsAPI.listDocs();
      const mappedDocs = data.files.map((file, idx) => {
        const ext = file.name.substring(file.name.lastIndexOf('.')).toUpperCase().replace('.', '');
        const sizeStr = file.size_bytes > 1024 * 1024 
          ? `${(file.size_bytes / (1024 * 1024)).toFixed(1)} MB` 
          : `${(file.size_bytes / 1024).toFixed(0)} KB`;
        
        const dateStr = file.updated 
          ? new Date(file.updated).toLocaleDateString('id-ID', { day: 'numeric', month: 'short', year: 'numeric' })
          : '-';

        return {
          id: file.md5_hash || `${file.name}-${idx}`,
          name: file.name,
          type: ext,
          date: dateStr,
          size: sizeStr,
          status: "INDEXED",
          rawSize: file.size_bytes,
        };
      });
      setDocuments(mappedDocs);
    } catch (error) {
      console.error("Gagal memuat dokumen:", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

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

  // Core file upload
  const handleFiles = async (fileList) => {
    setIsLoading(true);
    let successCount = 0;
    for (let i = 0; i < fileList.length; i++) {
      const file = fileList[i];
      try {
        await docsAPI.uploadDoc(file);
        successCount++;
      } catch (error) {
        console.error(`Gagal upload file ${file.name}:`, error);
        showCustomAlert("Gagal Upload", `Gagal mengunggah file ${file.name}: ${error.message || error}`, "error");
      }
    }
    if (successCount > 0) {
      showCustomAlert("Berhasil Upload", `${successCount} file berhasil diunggah dan di-embed ke sistem.`, "success");
      fetchDocuments();
    }
    setIsLoading(false);
  };

  // Delete Action
  const handleDelete = async (id, name) => {
    setCustomModal({
      isOpen: true,
      title: "Hapus Dokumen?",
      message: `Apakah Anda yakin ingin menghapus dokumen "${name}"? Tindakan ini juga akan menghapus seluruh data embedding terkait dan tidak dapat dibatalkan.`,
      type: "confirm",
      onConfirm: async () => {
        setCustomModal(prev => ({ ...prev, isOpen: false }));
        setIsLoading(true);
        try {
          await docsAPI.deleteDoc(name);
          showCustomAlert("Berhasil Dihapus", `Dokumen "${name}" berhasil dihapus dari cloud storage dan database.`, "success");
          fetchDocuments();
        } catch (error) {
          console.error(`Gagal menghapus dokumen ${name}:`, error);
          showCustomAlert("Gagal Menghapus", `Gagal menghapus dokumen: ${error.message || error}`, "error");
        } finally {
          setIsLoading(false);
        }
      },
      onCancel: () => {
        setCustomModal(prev => ({ ...prev, isOpen: false }));
      }
    });
  };

  // Download Action
  const handleDownload = async (name) => {
    try {
      await docsAPI.downloadDoc(name);
    } catch (error) {
      console.error(`Gagal mendownload dokumen ${name}:`, error);
      showCustomAlert("Gagal Download", `Gagal mengunduh dokumen: ${error.message || error}`, "error");
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
                              className="kb-action-btn download" 
                              title="Download Dokumen"
                              style={{ color: "#3b82f6" }}
                              onClick={() => handleDownload(doc.name)}
                            >
                              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                                <polyline points="7 10 12 15 17 10" />
                                <line x1="12" y1="15" x2="12" y2="3" />
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
                  <span className="kb-doc-content-title">Status Indeksasi</span>
                  <pre className="kb-doc-content-box" style={{ fontFamily: "inherit" }}>
                    File ini telah diunggah dan terindeks dengan aman di cloud storage. 
                    Anda dapat mengunduh file asli menggunakan tombol "Download" di bawah ini.
                  </pre>
                </div>
              </div>
              
              <div className="kb-modal-footer">
                <button type="button" className="kb-btn-primary" onClick={() => handleDownload(selectedDoc.name)} style={{ marginRight: "10px", backgroundColor: "#3b82f6", color: "#fff", border: "none", padding: "8px 16px", borderRadius: "4px", cursor: "pointer" }}>
                  📥 Download Dokumen
                </button>
                <button type="button" className="kb-btn-secondary" onClick={closeModal}>
                  Tutup
                </button>
              </div>

            </div>
          </div>
        )}

        {/* Custom Confirmation / Alert Modal */}
        {customModal.isOpen && (
          <div className="kb-modal-overlay" onClick={() => {
            if (customModal.type !== 'confirm' && customModal.onConfirm) {
              customModal.onConfirm();
            }
          }}>
            <div className="kb-modal-content custom-dialog" onClick={(e) => e.stopPropagation()} style={{ maxWidth: "450px" }}>
              
              <div className="kb-modal-header" style={{ borderBottom: "none", paddingBottom: "10px" }}>
                <h3 className="kb-modal-title" style={{ display: "flex", alignItems: "center", gap: "10px" }}>
                  {customModal.type === 'confirm' && <span style={{ color: '#ef4444', fontSize: '22px' }}>⚠️</span>}
                  {customModal.type === 'success' && <span style={{ color: '#10b981', fontSize: '22px' }}>✅</span>}
                  {customModal.type === 'error' && <span style={{ color: '#ef4444', fontSize: '22px' }}>❌</span>}
                  {customModal.type === 'info' && <span style={{ color: '#3b82f6', fontSize: '22px' }}>ℹ️</span>}
                  {customModal.title}
                </h3>
              </div>

              <div className="kb-modal-body" style={{ paddingTop: "10px", paddingBottom: "24px" }}>
                <p style={{ margin: 0, color: "#94a3b8", fontSize: "14px", lineHeight: "1.6" }}>
                  {customModal.message}
                </p>
              </div>

              <div className="kb-modal-footer" style={{ borderTop: "1px solid #1e293b", padding: "16px 24px" }}>
                {customModal.type === 'confirm' ? (
                  <>
                    <button 
                      type="button" 
                      className="kb-btn-secondary" 
                      onClick={customModal.onCancel}
                      style={{ padding: "8px 16px", borderRadius: "6px" }}
                    >
                      Batal
                    </button>
                    <button 
                      type="button" 
                      className="kb-btn-primary" 
                      onClick={customModal.onConfirm}
                      style={{ 
                        backgroundColor: "#ef4444", 
                        color: "#fff", 
                        border: "none", 
                        padding: "8px 16px", 
                        borderRadius: "6px", 
                        cursor: "pointer", 
                        fontWeight: "500",
                        transition: "background 0.2s" 
                      }}
                      onMouseOver={(e) => e.target.style.backgroundColor = "#dc2626"}
                      onMouseOut={(e) => e.target.style.backgroundColor = "#ef4444"}
                    >
                      Ya, Hapus
                    </button>
                  </>
                ) : (
                  <button 
                    type="button" 
                    className="kb-btn-primary" 
                    onClick={customModal.onConfirm}
                    style={{ 
                      backgroundColor: "#3b82f6", 
                      color: "#fff", 
                      border: "none", 
                      padding: "8px 16px", 
                      borderRadius: "6px", 
                      cursor: "pointer", 
                      fontWeight: "500",
                      transition: "background 0.2s"
                    }}
                    onMouseOver={(e) => e.target.style.backgroundColor = "#2563eb"}
                    onMouseOut={(e) => e.target.style.backgroundColor = "#3b82f6"}
                  >
                    OK
                  </button>
                )}
              </div>

            </div>
          </div>
        )}

      </div>
    </DashboardLayout>
  );
}

export default KnowledgeBase;
