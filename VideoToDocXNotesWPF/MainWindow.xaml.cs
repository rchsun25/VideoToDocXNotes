using Microsoft.Win32;
using System.Diagnostics;
using System.IO;
using System.Windows;

namespace VideoToDocXNotesWPF
{
    public partial class MainWindow : Window
    {
        public MainWindow()
        {
            InitializeComponent();
        }

        private void OnSelectFile(object sender, RoutedEventArgs e)
        {
            var dlg = new OpenFileDialog
            {
                Filter = "Video/Audio Files|*.mp4;*.mkv;*.mp3|Transcript|*.txt;*.docx",
                Multiselect = false
            };

            if (dlg.ShowDialog() == true)
            {
                RunPythonProcess(dlg.FileName);
            }
        }

        private void RunPythonProcess(string filePath)
        {
            var startInfo = new ProcessStartInfo
            {
                FileName = "python",
                Arguments = $"{Path.Combine(Directory.GetCurrentDirectory(), "AudioTranscriber.py")} \"{filePath}\"",
                UseShellExecute = false,
                RedirectStandardOutput = true,
                RedirectStandardError = true
            };

            using var process = new Process { StartInfo = startInfo };
            process.OutputDataReceived += (s, e) => { if (!string.IsNullOrEmpty(e.Data)) AppendOutput(e.Data); };
            process.ErrorDataReceived += (s, e) => { if (!string.IsNullOrEmpty(e.Data)) AppendOutput(e.Data); };
            process.Start();
            process.BeginOutputReadLine();
            process.BeginErrorReadLine();
        }

        private void AppendOutput(string text)
        {
            Dispatcher.Invoke(() =>
            {
                MessageBox.Show(text);
            });
        }
    }
}
