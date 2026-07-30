import { useState, useEffect } from 'react';
import { Mail, Phone, MessageCircle, Download, BookOpen, ChevronDown, ChevronRight, ExternalLink, HelpCircle } from 'lucide-react';
import api from '../api/axios';
import Spinner from '../components/ui/Spinner';
import Card from '../components/ui/Card';
import Button from '../components/ui/Button';

export default function Support() {
  const [content, setContent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('contact');
  const [openFaq, setOpenFaq] = useState(null);

  useEffect(() => {
    api.get('/support').then(({ data }) => setContent(data.data || {})).catch(() => {}).finally(() => setLoading(false));
  }, []);

  if (loading) return <div className="flex justify-center py-20"><Spinner size="lg" /></div>;

  const tabs = [
    { id: 'contact', label: 'Contact', icon: Mail },
    { id: 'links', label: 'Links', icon: ExternalLink },
    { id: 'faq', label: 'FAQ', icon: HelpCircle },
    { id: 'api-guide', label: 'API Guide', icon: BookOpen },
  ];

  return (
    <div className="max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold text-text-primary mb-6">Support</h1>

      {/* Tabs */}
      <div className="flex gap-1 bg-bg-tertiary rounded-lg p-1 mb-6">
        {tabs.map(t => (
          <button
            key={t.id}
            onClick={() => setActiveTab(t.id)}
            className={`flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === t.id ? 'bg-primary text-black' : 'text-text-secondary hover:text-text-primary'
            }`}
          >
            <t.icon size={15} /> {t.label}
          </button>
        ))}
      </div>

      {/* Contact Tab */}
      {activeTab === 'contact' && (
        <div className="space-y-4">
          <Card>
            <h2 className="text-lg font-semibold text-text-primary mb-4">Get in Touch</h2>
            <p className="text-text-secondary text-sm mb-6">Reach out to us through any of the channels below. We're here to help.</p>
            <div className="space-y-4">
              {content?.supportEmail && (
                <a href={`mailto:${content.supportEmail}`} className="flex items-center gap-4 p-4 bg-bg-tertiary rounded-xl hover:bg-border transition-colors">
                  <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center"><Mail size={20} className="text-primary" /></div>
                  <div><p className="text-sm font-medium text-text-primary">Email</p><p className="text-xs text-text-muted">{content.supportEmail}</p></div>
                </a>
              )}
              {content?.supportPhone && (
                <a href={`tel:${content.supportPhone}`} className="flex items-center gap-4 p-4 bg-bg-tertiary rounded-xl hover:bg-border transition-colors">
                  <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center"><Phone size={20} className="text-primary" /></div>
                  <div><p className="text-sm font-medium text-text-primary">Phone</p><p className="text-xs text-text-muted">{content.supportPhone}</p></div>
                </a>
              )}
              {content?.supportWhatsApp && (
                <a href={`https://wa.me/${content.supportWhatsApp.replace(/\D/g, '')}`} target="_blank" rel="noopener noreferrer" className="flex items-center gap-4 p-4 bg-bg-tertiary rounded-xl hover:bg-border transition-colors">
                  <div className="w-10 h-10 bg-green-500/10 rounded-lg flex items-center justify-center"><MessageCircle size={20} className="text-green-500" /></div>
                  <div><p className="text-sm font-medium text-text-primary">WhatsApp</p><p className="text-xs text-text-muted">{content.supportWhatsApp}</p></div>
                </a>
              )}
              {!content?.supportEmail && !content?.supportPhone && !content?.supportWhatsApp && (
                <p className="text-text-muted text-sm text-center py-8">Contact information not available yet.</p>
              )}
            </div>
          </Card>
        </div>
      )}

      {/* Links Tab */}
      {activeTab === 'links' && (
        <div className="space-y-4">
          <Card>
            <h2 className="text-lg font-semibold text-text-primary mb-4">Useful Links</h2>
            <div className="space-y-3">
              {content?.appDownloadUrl && (
                <a href={content.appDownloadUrl} target="_blank" rel="noopener noreferrer" className="flex items-center gap-4 p-4 bg-bg-tertiary rounded-xl hover:bg-border transition-colors">
                  <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center"><Download size={20} className="text-primary" /></div>
                  <div className="flex-1"><p className="text-sm font-medium text-text-primary">Download Mobile App</p><p className="text-xs text-text-muted">Get the Android app</p></div>
                  <ExternalLink size={16} className="text-text-muted" />
                </a>
              )}
              {content?.docsUrl && (
                <a href={content.docsUrl} target="_blank" rel="noopener noreferrer" className="flex items-center gap-4 p-4 bg-bg-tertiary rounded-xl hover:bg-border transition-colors">
                  <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center"><BookOpen size={20} className="text-primary" /></div>
                  <div className="flex-1"><p className="text-sm font-medium text-text-primary">Documentation</p><p className="text-xs text-text-muted">API reference and guides</p></div>
                  <ExternalLink size={16} className="text-text-muted" />
                </a>
              )}
              {!content?.appDownloadUrl && !content?.docsUrl && (
                <p className="text-text-muted text-sm text-center py-8">No links available yet.</p>
              )}
            </div>
          </Card>
        </div>
      )}

 {/* FAQ Tab */}
{activeTab === 'faq' && (
  <div className="space-y-3">
    {content?.faq?.length > 0 ? (
      content.faq.map((item, i) => (
        <Card key={i}>
          <button
            className="w-full flex items-center justify-between text-left"
            onClick={() => setOpenFaq(openFaq === i ? null : i)}
          >
            <h3 className="text-sm font-medium text-text-primary pr-4">{item.question}</h3>
            {openFaq === i ? <ChevronDown size={16} className="text-text-muted shrink-0" /> : <ChevronRight size={16} className="text-text-muted shrink-0" />}
          </button>
          {openFaq === i && <p className="text-sm text-text-secondary mt-3 leading-relaxed">{item.answer}</p>}
        </Card>
      ))
    ) : (
      <Card><p className="text-text-muted text-sm text-center py-8">No FAQs available yet.</p></Card>
    )}
  </div>
)}

      {/* API Guide Tab */}
      {activeTab === 'api-guide' && (
        <Card>
          <h2 className="text-lg font-semibold text-text-primary mb-4">API Integration Guide</h2>
          {content?.apiGuide ? (
            <div className="prose prose-sm prose-invert max-w-none">
              <pre className="bg-bg-tertiary rounded-xl p-4 text-sm text-text-secondary whitespace-pre-wrap font-sans leading-relaxed">{content.apiGuide}</pre>
            </div>
          ) : (
            <p className="text-text-muted text-sm text-center py-8">API guide not available yet.</p>
          )}
        </Card>
      )}
    </div>
  );
}