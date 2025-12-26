import React, { useState, useEffect } from 'react';
import { Issue } from '../services/ApiService';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import Sidebar from '@/components/layout/Sidebar';
import { User, Download, Edit2, Save, X } from 'lucide-react';
import { NotificationBell } from '@/components/NotificationBell';
import ApiService from '@/services/ApiService';
import { Link } from 'react-router-dom';
import { getInitials } from '@/utils/userUtils';
import { getUserData } from '@/utils/authUtils';
import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';

// Replace 'any' with a specific type for autoTable options
interface AutoTableOptions {
  head: string[][];
  body: string[][];
  theme?: string;
}

declare module 'jspdf' {
  interface jsPDF {
    autoTable: (options: AutoTableOptions) => void;
    lastAutoTable: {
      finalY: number;
    };
  }
}

interface Achievement {
  id: string;
  title: string;
  description: string;
  location: string;
  posted_date: string;
  image_posted: string;
  image_completed: string;
  achievement?: string;
}

const Achievements = () => {
  const [achievements, setAchievements] = useState<Achievement[]>([]);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editText, setEditText] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAchievements();
  }, []);

  const fetchAchievements = async () => {
    try {
      setLoading(true);
      // Get officer ID for filtering
      const user = getUserData();
      const officerId = user?.id;
      
      // Fetch from achievements API endpoint with officer filter
      let url = 'http://localhost:5000/api/notifications/achievements';
      if (officerId) {
        url += `?officer_id=${officerId}`;
      }
      const response = await fetch(url);
      const data = await response.json();

      if (data.success) {
        const achievementsData = data.data.achievements || [];
        setAchievements(achievementsData.map((ach: any) => {
          // Helper function to format image URL
          const formatImageUrl = (image: string) => {
            if (!image) return '';
            // If it's already a base64 image or full URL, return as is
            if (image.startsWith('data:image') || image.startsWith('http')) {
              return image;
            }
            // Otherwise, it's a filename - prepend the backend URL
            return `http://localhost:5000/uploads/${image}`;
          };

          return {
            id: ach.post_id.toString(),
            title: ach.description?.substring(0, 50) || 'Road Issue Resolved',
            description: ach.description || '',
            location: ach.location || '',
            posted_date: ach.posted_date || '',
            image_posted: formatImageUrl(ach.before_image), // Format image URL properly
            image_completed: formatImageUrl(ach.after_image), // Format image URL properly
            achievement: 'Road issue successfully resolved and repaired by local authorities.'
          };
        }));
      }
    } catch (error) {
      console.error('Error fetching achievements:', error);
      setAchievements([]);
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (id: string, currentText: string) => {
    setEditingId(id);
    setEditText(currentText);
  };

  const handleSave = async (id: string) => {
    try {
      // Create a basic achievement object with the edited text as action taken
      const achievementUpdate = {
        governmentOfficialName: 'Updated Official',
        designation: 'Officer',
        meetingDate: new Date().toISOString().split('T')[0],
        issueStatus: 'Completed',
        actionTaken: editText,
      };

      await ApiService.updateAchievement(id, achievementUpdate);

      // Update local state
      setAchievements(prev => prev.map(achievement =>
        achievement.id === id
          ? { ...achievement, achievement: editText }
          : achievement
      ));

      setEditingId(null);
      setEditText('');
    } catch (error) {
      console.error('Error saving achievement:', error);
      alert('Failed to save achievement. Please try again.');
    }
  };

  const handleCancel = () => {
    setEditingId(null);
    setEditText('');
  };

  const downloadReport = () => {
    try {
      const doc = new jsPDF();

      // Add header
      doc.setFontSize(20);
      doc.setTextColor(41, 128, 185);
      doc.text('VoiceUp - Achievements Report', 20, 25);

      // Add date
      doc.setFontSize(12);
      doc.setTextColor(100, 100, 100);
      doc.text(`Generated on: ${new Date().toLocaleDateString()}`, 20, 35);

      // Add summary
      doc.setTextColor(0, 0, 0);
      doc.text(`Total Achievements: ${achievements.length}`, 20, 45);

      // Prepare table data
      const tableData = achievements.map((item, index) => [
        (index + 1).toString(),
        item.description.substring(0, 50) + (item.description.length > 50 ? '...' : ''),
        item.location || 'N/A',
        item.posted_date || 'N/A',
        (item.achievement || 'No achievement details').substring(0, 40) +
        ((item.achievement || '').length > 40 ? '...' : '')
      ]);

      // Add table using autoTable
      autoTable(doc, {
        head: [['#', 'Issue Description', 'Location', 'Posted Date', 'Achievement']],
        body: tableData,
        startY: 55,
        theme: 'striped',
        headStyles: {
          fillColor: [41, 128, 185],
          textColor: 255,
          fontSize: 10,
          fontStyle: 'bold'
        },
        bodyStyles: {
          fontSize: 9,
          cellPadding: 3
        },
        columnStyles: {
          0: { cellWidth: 15 }, // #
          1: { cellWidth: 50 }, // Description
          2: { cellWidth: 35 }, // Location
          3: { cellWidth: 25 }, // Date
          4: { cellWidth: 50 }  // Achievement
        },
        margin: { left: 15, right: 15 }
      });

      // Add footer
      const pageHeight = doc.internal.pageSize.height;
      doc.setFontSize(10);
      doc.setTextColor(100, 100, 100);
      doc.text('This report contains completed road infrastructure achievements.', 20, pageHeight - 30);
      doc.text('Generated by VoiceUp - Community Issue Reporting Platform', 20, pageHeight - 20);

      // Save the PDF
      doc.save(`VoiceUp_Achievements_Report_${new Date().toISOString().split('T')[0]}.pdf`);

    } catch (error) {
      console.error('Error generating PDF:', error);
      // Fallback to simple text-based PDF
      const doc = new jsPDF();
      doc.setFontSize(16);
      doc.text('VoiceUp - Achievements Report', 20, 30);
      doc.setFontSize(12);
      doc.text(`Generated on: ${new Date().toLocaleDateString()}`, 20, 50);
      doc.text(`Total Achievements: ${achievements.length}`, 20, 70);

      let yPosition = 90;
      achievements.forEach((item, index) => {
        doc.text(`${index + 1}. ${item.description}`, 20, yPosition);
        doc.text(`   Location: ${item.location}`, 25, yPosition + 10);
        doc.text(`   Date: ${item.posted_date}`, 25, yPosition + 20);
        yPosition += 40;

        if (yPosition > 250) {
          doc.addPage();
          yPosition = 30;
        }
      });

      doc.save(`VoiceUp_Achievements_Report_${new Date().toISOString().split('T')[0]}.pdf`);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex">
        <Sidebar />
        <div className="flex-1 flex items-center justify-center">
          <div className="text-lg">Loading achievements...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex">
      <Sidebar />

      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="bg-white border-b border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-gray-800">Achievements</h1>
            <div className="flex items-center gap-4">
              <Button
                onClick={downloadReport}
                className="bg-blue-800 hover:bg-blue-900 text-white flex items-center gap-2 px-4 py-2"
              >
                <Download className="h-4 w-4" />
                Download Report
              </Button>
              <NotificationBell />
              <Link to="/officer-profile">
                <span className="bg-blue-600 text-white px-3 py-1 rounded-full text-sm font-bold cursor-pointer hover:bg-blue-700 transition-colors">
                  {getInitials(getUserData()?.username || 'User')}
                </span>
              </Link>
            </div>
          </div>
        </header>

        <main className="flex-1 p-6">
          {achievements.length === 0 ? (
            <div className="text-center text-gray-500 mt-12">
              <p>No achievements found. Complete some issues to see them here!</p>
            </div>
          ) : (
            <div className="bg-white rounded-lg shadow">
              {/* Table Header */}
              <div className="grid grid-cols-12 gap-4 p-4 border-b bg-gray-100 font-semibold text-sm text-gray-700 uppercase tracking-wide">
                <div className="col-span-3">Issue Description</div>
                <div className="col-span-2">Location</div>
                <div className="col-span-1">Posted Date</div>
                <div className="col-span-2">Image (Posted)</div>
                <div className="col-span-2">Image (Completed)</div>
                <div className="col-span-2">Achievement</div>
              </div>

              {/* Table Content */}
              <div className="divide-y">
                {achievements.map((achievement) => (
                  <div key={achievement.id} className="grid grid-cols-12 gap-4 p-4 items-center">
                    <div className="col-span-3">
                      <p className="text-sm text-gray-900">{achievement.description}</p>
                    </div>
                    <div className="col-span-2">
                      <p className="text-sm text-gray-600">{achievement.location}</p>
                    </div>
                    <div className="col-span-1">
                      <p className="text-sm text-gray-600">{achievement.posted_date}</p>
                    </div>
                    <div className="col-span-2">
                      <img
                        src={achievement.image_posted}
                        alt="Issue Posted"
                        className="w-20 h-16 object-cover rounded-md border border-gray-200"
                        onError={(e) => {
                          e.currentTarget.src = '/images/image 2.png';
                        }}
                      />
                    </div>
                    <div className="col-span-2">
                      {achievement.image_completed ? (
                        <img
                          src={achievement.image_completed}
                          alt="Issue Completed"
                          className="w-20 h-16 object-cover rounded-md border border-gray-200"
                          onError={(e) => {
                            e.currentTarget.style.display = 'none';
                            e.currentTarget.parentElement!.style.backgroundColor = '#000';
                          }}
                        />
                      ) : (
                        <div className="w-20 h-16 bg-black rounded-md border border-gray-200" title="No after image available" />
                      )}
                    </div>
                    <div className="col-span-2">
                      {editingId === achievement.id ? (
                        <div className="flex gap-2">
                          <textarea
                            value={editText}
                            onChange={(e) => setEditText(e.target.value)}
                            className="flex-1 p-2 border border-gray-300 rounded text-sm resize-none"
                            rows={2}
                            placeholder="Add achievement details..."
                          />
                          <div className="flex flex-col gap-1">
                            <Button
                              size="sm"
                              onClick={() => handleSave(achievement.id)}
                              className="bg-green-600 hover:bg-green-700 text-white p-1"
                            >
                              <Save className="h-3 w-3" />
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={handleCancel}
                              className="p-1"
                            >
                              <X className="h-3 w-3" />
                            </Button>
                          </div>
                        </div>
                      ) : (
                        <div className="flex items-center gap-2">
                          <p className="text-sm text-gray-900 flex-1">
                            {achievement.achievement || 'No achievement details added'}
                          </p>
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => handleEdit(achievement.id, achievement.achievement || '')}
                            className="p-1"
                          >
                            <Edit2 className="h-4 w-4" />
                          </Button>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

export default Achievements;