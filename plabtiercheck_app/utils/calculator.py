# 경기가 종료된 후
# 매니저의 결과가 들어오면
# 계산해서 리턴

# calculate.py
import math

from plabtiercheck_app.models import ManagerEvaluationSource, TeammateEvaluationSource, GPSDataSource, PostGameStatistics


def calculate_post_game_statistics(game_id):
    # 게임 ID를 기반으로 필요한 데이터를 가져옵니다.
    manager_data = ManagerEvaluationSource.objects.filter(related_game_id=game_id)
    teammate_data = TeammateEvaluationSource.objects.filter(related_game_id=game_id)
    gps_data = GPSDataSource.objects.filter(related_game_id=game_id)

    # 통계 계산 로직을 구현합니다.
    # 이 예시에서는 단순히 평균 값을 계산하는 것으로 대체하겠습니다.

    # Manager 평가 평균 계산
    manager_score_sum = 0
    for evaluation in manager_data:
        manager_score_sum += evaluation.score2  # 예시로 기술적 능력(score2)만 사용
    manager_score_average = manager_score_sum / len(manager_data) if len(manager_data) > 0 else 0

    # Teammate 평가 평균 계산
    teammate_score_sum = 0
    for evaluation in teammate_data:
        teammate_score_sum += evaluation.score2  # 예시로 기술적 능력(score2)만 사용
    teammate_score_average = teammate_score_sum / len(teammate_data) if len(teammate_data) > 0 else 0

    # GPS 데이터 기반 통계 계산
    total_distance_covered = 0
    for gps in gps_data:
        total_distance_covered += gps.distance_covered

    # 계산된 결과를 PostGameStatistics 모델에 저장
    post_game_stats = PostGameStatistics(
        player_id=game_id,  # 게임 ID와 관련된 플레이어
        manager_referee_score=manager_score_average,
        average_teammate_score=teammate_score_average,
        distance_covered=total_distance_covered,
        # 다른 필드 설정
    )
    post_game_stats.save()

    return post_game_stats


def calculate_area(lat, lon):
    EARTH_RADIUS = 6371000
    distance = 100 / 2
    rad_lat = math.radians(lat)

    lat_change = math.degrees(distance / EARTH_RADIUS)
    lon_change = math.degrees(distance / (EARTH_RADIUS * math.cos(rad_lat)))

    lat_upper = lat + lat_change
    lat_lower = lat - lat_change
    lon_upper = lon + lon_change
    lon_lower = lon - lon_change

    return {
        'lat_upper': lat_upper,
        'lat_lower': lat_lower,
        'lon_upper': lon_upper,
        'lon_lower': lon_lower
    }


# gps 연결시 게임생성? 같은 장소에 존재하는 플레이어의 게임시간이 모두 달라질 수도?