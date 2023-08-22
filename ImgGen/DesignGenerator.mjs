import { writeFileSync } from 'fs';
import { join, dirname } from 'path';
import fetch from 'node-fetch';
import { fileURLToPath } from 'url'; // To convert import.meta.url to a file path


const YOUR_API_KEY = '519161fafc5ee70b9d2486b87acfe438332629e5fcf762bd1d7970670ea867ffe6b3bca104ffc8fb6314a35327bde222';

const generateRandomName = () => {
  const randomString = Math.random().toString(36).substring(7);
  return `output_${randomString}.png`;
};

const generateImage = async () => {
  const formGenerate = new FormData();
  formGenerate.append('prompt', 'tattoo design, stencil, tattoo stencil, traditional, white background, a snake surrounded by flowers');

  const generateResponse = await fetch('https://clipdrop-api.co/text-to-image/v1', {
    method: 'POST',
    headers: {
      'x-api-key': YOUR_API_KEY,
    },
    body: formGenerate,
  });

  const generateBuffer = await generateResponse.arrayBuffer();
  return generateBuffer;
};

const removeBackground = async (imageBuffer) => {
  const formRemoveBackground = new FormData();
  const imageBlob = new Blob([imageBuffer], { type: 'image/png' });
  formRemoveBackground.append('image_file', imageBlob, 'generated_image.png');

  const removeBackgroundResponse = await fetch('https://clipdrop-api.co/remove-background/v1', {
    method: 'POST',
    headers: {
      'x-api-key': YOUR_API_KEY,
    },
    body: formRemoveBackground,
  });

  const removeBackgroundBuffer = await removeBackgroundResponse.arrayBuffer();
  return removeBackgroundBuffer;
};

const runPipeline = async () => {
  try {
    const generatedImageBuffer = await generateImage();
    // const imageWithRemovedBackground = await removeBackground(generatedImageBuffer);

    const outputFileName = generateRandomName();
    const currentFilePath = fileURLToPath(import.meta.url); // Convert import.meta.url to file path
    const outputPath = join(dirname(currentFilePath), outputFileName);

    // writeFileSync(outputPath, Buffer.from(imageWithRemovedBackground));
    writeFileSync(outputPath, Buffer.from(generatedImageBuffer));

    console.log(`Image saved as ${outputFileName}`);
  } catch (error) {
    console.error('Error in pipeline:', error);
  }
};

runPipeline();
