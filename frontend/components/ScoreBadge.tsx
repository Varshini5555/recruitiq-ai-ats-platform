interface Props {
  score: number;
}

export default function ScoreBadge({ score }: Props) {

  let color = "bg-red-500";

  if (score >= 80) color = "bg-green-500";
  else if (score >= 60) color = "bg-yellow-500";

  return (
    <div className="flex flex-col items-center justify-center">

      <div
        className={`w-32 h-32 rounded-full ${color}
        flex items-center justify-center
        text-white text-3xl font-bold shadow-xl`}
      >
        {Math.round(score)}
      </div>

      <p className="mt-3 text-sm text-gray-500">
        Score
      </p>

    </div>
  );
}