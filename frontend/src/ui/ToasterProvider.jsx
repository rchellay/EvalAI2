import { Toaster } from 'react-hot-toast';
export default function ToasterProvider() {
  return <Toaster position="top-right" toastOptions={{ style:{ background:'#1e293b', color:'#f1f5f9'} }} />;
}
