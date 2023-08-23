import { writeFileSync } from "fs";
import { join, dirname } from "path";
import fetch from "node-fetch";
import { fileURLToPath } from "url"; // To convert import.meta.url to a file path

const YOUR_API_KEY =
  "229dd823c184d5793446c72cf457565c9f26903656fef04aef9605aa8d28605df05ff156e2b16b9444eb538cb762b8d4";

const generateRandomName = () => {
  const randomString = Math.random().toString(36).substring(7);
  return `output_${randomString}.png`;
};

const generateImage = async () => {
  const formGenerate = new FormData();
  formGenerate.append(
    "prompt",
    "tattoo design, stencil, tattoo stencil, stencil over white background, realistic, head of a vampire bat with bloody fangs"
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
    // const outputFileName = 'Tattoo.png';
    const currentFilePath = fileURLToPath(import.meta.url); // Convert import.meta.url to file path
    const outputPath = join(dirname(currentFilePath), outputFileName);

    // writeFileSync(outputPath, Buffer.from(imageWithRemovedBackground));
    writeFileSync(outputPath, Buffer.from(generatedImageBuffer));

    console.log(`Image saved as ${outputFileName}`);
  } catch (error) {
    console.error("Error in pipeline:", error);
  }
};

runPipeline();
