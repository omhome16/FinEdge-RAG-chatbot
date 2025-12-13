import { useState } from 'react';
import { Upload, FileText, CheckCircle, AlertCircle } from 'lucide-react';
import { Button } from './ui/Button';
import { uploadFile } from '../api';
import { cn } from '../utils';

export const FileUploader: React.FC<{ onUploadComplete: () => void }> = ({ onUploadComplete }) => {
    const [isDragging, setIsDragging] = useState(false);
    const [file, setFile] = useState<File | null>(null);
    const [uploading, setUploading] = useState(false);
    const [status, setStatus] = useState<'idle' | 'success' | 'error'>('idle');

    const handleDragOver = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = () => {
        setIsDragging(false);
    };

    const handleDrop = (e: React.DragEvent) => {
        e.preventDefault();
        setIsDragging(false);
        if (e.dataTransfer.files?.[0]) {
            setFile(e.dataTransfer.files[0]);
        }
    };

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        if (e.target.files?.[0]) {
            setFile(e.target.files[0]);
        }
    };

    const handleUpload = async () => {
        if (!file) return;
        setUploading(true);
        try {
            await uploadFile(file);
            setStatus('success');
            onUploadComplete();
        } catch (error) {
            console.error(error);
            setStatus('error');
        } finally {
            setUploading(false);
        }
    };

    return (
        <div className="w-full max-w-md mx-auto p-6 bg-white rounded-xl shadow-md border border-gray-100">
            <h3 className="text-lg font-semibold mb-4 text-gray-800">Upload Financial Documents</h3>

            <div
                className={cn(
                    "border-2 border-dashed rounded-xl p-8 flex flex-col items-center justify-center transition-colors cursor-pointer bg-gray-50",
                    isDragging ? "border-accent bg-accent/5" : "border-gray-300 hover:border-gray-400"
                )}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                onClick={() => document.getElementById('file-input')?.click()}
            >
                <input
                    id="file-input"
                    type="file"
                    className="hidden"
                    accept=".pdf"
                    onChange={handleFileSelect}
                />
                {file ? (
                    <div className="flex flex-col items-center text-center">
                        <FileText className="w-12 h-12 text-blue-500 mb-2" />
                        <p className="font-medium text-gray-900">{file.name}</p>
                        <p className="text-sm text-gray-500">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                    </div>
                ) : (
                    <div className="flex flex-col items-center text-center">
                        <Upload className="w-12 h-12 text-gray-400 mb-2" />
                        <p className="font-medium text-gray-700">Click to upload or drag and drop</p>
                        <p className="text-sm text-gray-500">PDF files only</p>
                    </div>
                )}
            </div>

            {status === 'error' && (
                <div className="mt-4 flex items-center text-error bg-error/10 p-3 rounded-lg">
                    <AlertCircle className="w-5 h-5 mr-2" />
                    <span>Upload failed. Please try again.</span>
                </div>
            )}

            {status === 'success' && (
                <div className="mt-4 flex items-center text-success bg-success/10 p-3 rounded-lg">
                    <CheckCircle className="w-5 h-5 mr-2" />
                    <span>Document processed successfully!</span>
                </div>
            )}

            {file && status !== 'success' && (
                <Button
                    onClick={(e) => { e.stopPropagation(); handleUpload(); }}
                    className="w-full mt-4"
                    disabled={uploading}
                >
                    {uploading ? "Processing..." : "Analyze Document"}
                </Button>
            )}
        </div>
    );
};
