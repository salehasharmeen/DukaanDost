import 'dart:io';
import 'package:dio/dio.dart';
import 'package:record/record.dart';
import 'package:path_provider/path_provider.dart';
import 'package:permission_handler/permission_handler.dart';
import '../core/api_client.dart';

class VoiceService {
  static final AudioRecorder _recorder = AudioRecorder();
  static String? _filePath;

  /// Request mic permission explicitly before recording
  static Future<void> _requestPermission() async {
    final status = await Permission.microphone.request();
    if (!status.isGranted) {
      throw Exception(
        'Microphone permission denied. Please allow mic access in your phone settings.',
      );
    }
  }

  /// Start recording to a temp WAV file
  static Future<void> startRecording() async {
    await _requestPermission();

    final dir = await getTemporaryDirectory();
    _filePath = '${dir.path}/voice_input.wav';

    await _recorder.start(
      const RecordConfig(
        encoder: AudioEncoder.wav,
        sampleRate: 16000,
        numChannels: 1,
      ),
      path: _filePath!,
    );
  }

  /// Stop recording and POST the file to /transcribe/
  static Future<Map<String, dynamic>> stopAndTranscribe() async {
    final path = await _recorder.stop();
    if (path == null) throw Exception('Recording failed — no file produced');

    final file = File(path);
    if (!file.existsSync()) {
      throw Exception('Audio file not found at $path');
    }

    final formData = FormData.fromMap({
      'file': await MultipartFile.fromFile(
        file.path,
        filename: 'voice_input.wav',
      ),
    });

    final res = await ApiClient.instance.post(
      '/transcribe/',
      data: formData,
      options: Options(contentType: 'multipart/form-data'),
    );

    return res.data as Map<String, dynamic>;
  }

  /// Cancel recording without uploading
  static Future<void> cancelRecording() async {
    await _recorder.cancel();
  }

  static Future<bool> isRecording() => _recorder.isRecording();
}