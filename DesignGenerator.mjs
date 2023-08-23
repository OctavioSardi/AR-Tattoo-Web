import { writeFileSync } from "fs";
import { join, dirname } from "path";
import fetch from "node-fetch";
import { fileURLToPath } from "url"; // To convert import.meta.url to a file path
import sharp from "sharp";

const YOUR_API_KEY =
  "YOUR API KEY";

const generateRandomName = () => {
  const randomString = Math.random().toString(36).substring(7);
  return `output_${randomString}.png`;
};

const generateImage = async () => {
  const formGenerate = new FormData();
  formGenerate.append(
    "prompt",
    "tattoo design, stencil, tattoo stencil, tattoo stencil over white background, tribal, snake surrounded by clouds"
  );

  const generateResponse = await fetch(
    "https://clipdrop-api.co/text-to-image/v1",
    {
      method: "POST",
      headers: {
        "x-api-key": YOUR_API_KEY,
      },
      body: formGenerate,
    }
  );

  const generateBuffer = await generateResponse.arrayBuffer();
  return generateBuffer;
};

const removeBackground = async (imageBuffer) => {
  const formRemoveBackground = new FormData();
  const imageBlob = new Blob([imageBuffer], {
    type: "image/png",
  });
  formRemoveBackground.append("image_file", imageBlob, "generated_image.png");

  const removeBackgroundResponse = await fetch(
    "https://clipdrop-api.co/remove-background/v1",
    {
      method: "POST",
      headers: {
        "x-api-key": YOUR_API_KEY,
      },
      body: formRemoveBackground,
    }
  );

  const removeBackgroundBuffer = await removeBackgroundResponse.arrayBuffer();
  return removeBackgroundBuffer;
};

const runPipeline = async () => {
  try {
    const generatedImageBuffer = await generateImage();
    // const imageWithRemovedBackground = await removeBackground(generatedImageBuffer);


    const outputFileName = generateRandomName();
    const currentFilePath = fileURLToPath(import.meta.url);
    const outputPath = join(dirname(currentFilePath), outputFileName);

    // write the original image to file
    writeFileSync(outputPath, Buffer.from(generatedImageBuffer));
    console.log(`Original image saved as ${outputFileName}`);

    // Read the image from the file and resize it
    const originalImageBuffer = await sharp(outputPath).toBuffer();
    const resizedImageBuffer = await sharp(originalImageBuffer)
      .resize(512, 512) // Resize to 128x128 pixels
      .toBuffer();

    // Overwrite the file with the resized image
    writeFileSync(outputPath, Buffer.from(resizedImageBuffer));
    console.log(`Resized image saved as ${outputFileName}`);
  } catch (error) {
    console.error("Error in pipeline:", error);
  }
};

runPipeline();
